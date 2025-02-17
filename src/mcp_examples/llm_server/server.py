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
from loguru import logger
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("math")

load_dotenv()  # load environment variables from .env

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


@mcp.tool()
async def translate(target_language: str, text: str) -> str:
    """Translate the given text to the target language.

    Args:
        target_language: The target language
        text: The text to translate
    """
    logger.info(f"Translating text to {target_language}: {text}")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            f"Translate the following text to {target_language}: {text}"],
    )
    return response.text


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
