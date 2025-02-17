import asyncio
import os
import sys
from contextlib import AsyncExitStack
from datetime import timedelta
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types as genai_types
from loguru import logger
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from mcp_examples.utils import to_gemini_tool

load_dotenv()  # load environment variables from .env


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server

        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")

        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command, args=[server_script_path], env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write,
                          read_timeout_seconds=timedelta(seconds=300))
        )

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        logger.debug(
            f"Connected to server with tools: {[tool.name for tool in tools]}")
        print("\nConnected to server with tools:",
              [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools"""
        # messages = [{"role": "user", "content": query}]

        messages = [
            genai_types.Content(
                role="user", parts=[genai_types.Part.from_text(text=query)]
            )
        ]

        response = await self.session.list_tools()
        genai_tools = [to_gemini_tool(tool) for tool in response.tools]

        # Initial Claude API call
        response = self.gemini.models.generate_content(
            model="gemini-2.0-flash",
            contents=messages,
            config=genai_types.GenerateContentConfig(
                tools=genai_tools,
                automatic_function_calling=genai_types.AutomaticFunctionCallingConfig(
                    disable=False,
                ),
            ),
        )
        logger.debug(f"Response: {response}")

        # Process response and handle tool calls
        final_text = []
        tool_results = []
        if response.candidates:
            for candidate in response.candidates:
                if candidate.content:
                    for part in candidate.content.parts:
                        if part.text:
                            final_text.append(part.text)
                        elif part.function_call:
                            tool_name = part.function_call.name
                            tool_args = part.function_call.args

                            if self.session:
                                # Execute tool call
                                result = await self.session.call_tool(
                                    tool_name, tool_args
                                )
                                tool_results.append(
                                    {"call": tool_name, "result": result}
                                )
                                final_text.append(
                                    f"[Calling tool {tool_name} with args {tool_args}, result: {result}]"
                                )
                                logger.debug(
                                    f"Tool {tool_name} called with args {tool_args}, result: {result}"
                                )
                            else:
                                final_text.append(
                                    "Error: No active session to call tool."
                                )
        else:
            final_text.append("No candidates in response.")
        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)
            # pylint: disable=broad-exception-caught
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())
