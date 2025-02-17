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

from typing import List, Optional

from duckduckgo_search import DDGS
from pydantic import BaseModel, Field


class DuckDuckGoSearchResult(BaseModel):
    title: str = Field(..., description="The title of the search result")
    href: str = Field(..., description="The URL of the search result")
    body: str = Field(..., description="The snippet of the search result")


async def asearch(
    query: str,
    max_results: int = 10,
    region: Optional[str] = None,
) -> List[DuckDuckGoSearchResult]:
    """
    Search the web for the given query.
    """
    extra_params = {}
    if region:
        extra_params["region"] = region
    results = DDGS().text(query, max_results=max_results, **extra_params)
    return [DuckDuckGoSearchResult.model_validate(result) for result in results]


def search(
    query: str,
    max_results: int = 10,
    region: Optional[str] = None,
) -> List[DuckDuckGoSearchResult]:
    """
    Search the web for the given query.

    Args:
      query: The query to search for.

    Returns:
      A list of search results.
    """
    extra_params = {}
    if region:
        extra_params["region"] = region
    results = DDGS().text(query, max_results=max_results, **extra_params)
    return [DuckDuckGoSearchResult.model_validate(result) for result in results]


if __name__ == "__main__":
    print(search("python programming"))
