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

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("math")


@mcp.tool()
async def add(a: float, b: float) -> float:
    """Add two floats.

    Args:
        a: The first float
        b: The second float
    """
    return a + b


@mcp.tool()
async def subtract(a: float, b: float) -> float:
    """Subtract two floats.

    Args:
        a: The first float
        b: The second float
    """
    return a - b


@mcp.tool()
async def multiply(a: float, b: float) -> float:
    """Multiply two floats.

    Args:
        a: The first float
        b: The second float
    """
    return a * b


@mcp.tool()
async def divide(a: float, b: float) -> float:
    """Divide two floats. Returns 0 if dividing by zero.

    Args:
        a: The first float
        b: The second float
    """
    if b == 0:
        return 0.0
    return a / b


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
