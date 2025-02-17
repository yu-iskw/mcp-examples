# Copyright 2025 yu-iskw
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from dotenv import load_dotenv
from google import genai
from mcp.server.fastmcp import FastMCP

from mcp_examples.agentic_server.agent import ResearchWorkflow, ResearchWorkflowState

# Initialize FastMCP server
mcp = FastMCP("math")

load_dotenv()  # load environment variables from .env

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# client = genai.Client(vertexai=True, location="us-central1")
graph_builder = ResearchWorkflow(genai_client=client).get_graph_builder()
graph = graph_builder.compile()


@mcp.tool()
async def research(research_topic: str) -> str:
    """Research the given topic.

    Args:
        research_topic: The topic to research
    """
    state = ResearchWorkflowState(research_topic=research_topic)
    response = await graph.ainvoke(state)
    return response["summary"]


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
