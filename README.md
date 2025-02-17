# MCP Examples

This repository provides a collection of examples demonstrating the usage of the MCP (Message Communication Protocol) framework. MCP is designed to facilitate the creation of modular and scalable applications, particularly in areas like agentic systems and LLM-powered tools. These examples are intended to help you understand the core concepts of MCP and how to build various types of applications using it.

## Set up

### Prerequisites

- [uv](https://astral.sh/uv) is required for fast package management.

### Install dependencies

```bash
uv venv
uv sync --all-extras

# Or, alternatively, use make
make setup
```

This will create a virtual environment and install all necessary dependencies for running the examples.

## Examples

The examples are categorized to showcase different aspects of MCP and its capabilities.

### Debug Client

We have a debugging MCP client with a MCP server.

```bash
uv run python src/mcp_examples/debug_mcp_client.py src/mcp_examples/agentic_server/server.py
```

### Simple Examples

- [src/mcp_examples/weather/server.py](src/mcp_examples/weather/server.py): This is the foundational example from the MCP framework documentation. It demonstrates the basic structure of an MCP server, including defining tools and running the server. It's a great starting point to understand the core components of an MCP application.
- [src/mcp_examples/math_tools/server.py](src/mcp_examples/math_tools/server.py): This example expands on the basics by showing how to integrate custom tools into your MCP server. It illustrates how to define and use your own functionalities within the MCP framework, making it adaptable to various tasks.

### SSE Server

- [src/mcp_examples/sse_server/server.py](src/mcp_examples/sse_server/server.py): This example demonstrates how to use the MCP framework to create a server that can send and receive events over a stream. It's a great starting point to understand how to build applications that can handle real-time data streams.
  - `uv python src/mcp_examples/sse_server/server.py --transport sse`

### Advanced Examples with LLM/Agent

MCP servers are versatile and can handle a wide range of tasks.
They are suitable for simple operations like calling APIs or fetching data from databases, but also powerful enough to orchestrate complex workflows involving LLMs and agents.
This flexibility makes them ideal for building applications ranging from basic data retrieval to sophisticated agentic systems.

- [src/mcp_examples/llm_server/server.py](src/mcp_examples/llm_server/server.py): This example demonstrates how to incorporate Large Language Models (LLMs) into an MCP server. It showcases how you can leverage the power of LLMs within the MCP framework to build intelligent applications that can process and generate natural language.
- [src/mcp_examples/agentic_server/server.py](src/mcp_examples/agentic_server/server.py): This advanced example illustrates the creation of agentic systems using MCP. It shows how to design and implement workflows for agents within the MCP framework, enabling you to build complex, autonomous applications that can perform tasks and interact with the environment.

## MCP Inspector

Please look into <https://github.com/modelcontextprotocol/inspector> for more information.

```bash
npx @modelcontextprotocol/inspector node build/index.js
```
