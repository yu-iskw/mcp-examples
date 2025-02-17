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

from google import genai
from google.genai import types as genai_types
from mcp import types as mcp_types


def to_gemini_tool(mcp_tool: mcp_types.Tool) -> genai_types.Tool:
    """
    Converts an MCP tool schema to a Gemini tool.

    Args:
        name: The name of the tool.
        description: The description of the tool.
        input_schema: The input schema of the tool.

    Returns:
        A Gemini tool.
    """
    required_params: list[str] = mcp_tool.inputSchema.get("required", [])
    properties = {}
    for key, value in mcp_tool.inputSchema.get("properties", {}).items():
        schema_dict = {
            "type": value.get("type", "STRING").upper(),
            "description": value.get("description", ""),
        }
        properties[key] = genai_types.Schema(**schema_dict)

    function = genai.types.FunctionDeclaration(
        name=mcp_tool.name,
        description=mcp_tool.description,
        parameters=genai.types.Schema(
            type="OBJECT",
            properties=properties,
            required=required_params,
        ),
    )
    return genai_types.Tool(function_declarations=[function])
