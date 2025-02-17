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

import asyncio
import os
import textwrap
from dataclasses import dataclass
from typing import List

from google import genai
from google.genai import types
from langgraph.graph import END, START, StateGraph
from loguru import logger
from pydantic import BaseModel, Field

from mcp_examples.tools.duckduckgo import DuckDuckGoSearchResult, search
from mcp_examples.utils import request_get


class PlannerResult(BaseModel):
    """The result of the planner."""

    search_queries: List[str] = Field(
        description="The search queries to research", default_factory=list
    )


class ResearchData(BaseModel):
    """The research data."""

    title: str = Field(..., description="The title of the research")
    href: str = Field(..., description="The href of the research")
    content: str = Field(..., description="The content of the research")


class ResearchWorkflowState(BaseModel):
    research_topic: str = Field(..., description="The topic to research")
    plan: PlannerResult = Field(
        description="The plan for the research", default_factory=PlannerResult
    )
    research_data: List[ResearchData] = Field(
        description="The research data", default_factory=list
    )
    summary: str = Field(description="The summary of the research", default="")


@dataclass
class ResearchWorkflow:
    genai_client: genai.Client

    def get_graph_builder(self) -> StateGraph:
        graph_builder = StateGraph(ResearchWorkflowState)
        # Add nodes
        graph_builder.add_node(
            "planner",
            self.planner,
        )
        graph_builder.add_node(
            "researcher",
            self.researcher,
        )
        graph_builder.add_node(
            "summarizer",
            self.summarizer,
        )
        # Add edges
        graph_builder.add_edge(START, "planner")
        graph_builder.add_edge("planner", "researcher")
        graph_builder.add_edge("researcher", "summarizer")
        graph_builder.add_edge("summarizer", END)
        return graph_builder

    def planner(self, state: ResearchWorkflowState) -> ResearchWorkflowState:
        logger.info(
            f"Planning the research for the topic: {state.research_topic}")
        system_prompt = textwrap.dedent(
            """
            You are an expert research planner specializing in crafting optimal search queries. Your task is to generate the most effective search queries to comprehensively research the given topic. Consider these guidelines:

            1. Create queries that will yield diverse, high-quality information sources
            2. Use specific keywords and phrases that precisely target the topic
            3. Include both broad and narrow focus queries to capture different aspects
            4. Structure queries to avoid bias and ensure balanced coverage
            5. Limit to a maximum of 5 queries that together provide complete coverage

            Return only the most essential queries that will produce the most valuable research results.
            """
        )
        contents = [
            system_prompt,
            state.research_topic,
        ]
        response = self.genai_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PlannerResult,
            ),
        )
        state.plan = response.parsed
        logger.info(f"Search queries: {state.plan.search_queries}")
        return state

    async def researcher(self, state: ResearchWorkflowState) -> ResearchWorkflowState:
        logger.info(f"Researching the topic: {state.research_topic}")
        research_data: List[ResearchData] = []
        semaphore = asyncio.Semaphore(20)

        async def fetch_research_data(search_result: DuckDuckGoSearchResult) -> ResearchData | None:
            async with semaphore:
                logger.info(
                    f"Researching the search result: {search_result.title} at {search_result.href}"
                )
                try:
                    response = await request_get(search_result.href)
                    return ResearchData(
                        title=search_result.title,
                        href=search_result.href,
                        content=response.text,
                    )
                # pylint: disable=broad-exception-caught
                except Exception as e:
                    logger.error(
                        f"Failed to get the content of the search result: {e}")
                    return None

        async def process_search_query(search_query: str) -> List[ResearchData]:
            tasks = []
            for _search_result in search(query=search_query, max_results=5):
                if _search_result.href.endswith("html"):
                    tasks.append(fetch_research_data(_search_result))
            results = await asyncio.gather(*tasks)
            return [result for result in results if result is not None]

        for search_query in state.plan.search_queries:
            data = await process_search_query(search_query)
            research_data.extend(data)
        state.research_data = research_data
        return state

    def summarizer(self, state: ResearchWorkflowState) -> ResearchWorkflowState:
        logger.info(f"Summarizing the research data: {state.research_data}")
        system_prompt = textwrap.dedent(
            """
            You are an expert research summarizer. Your task is to analyze and synthesize multiple research sources into a clear, concise, and well-structured summary. Follow these guidelines:

            1. Focus on key insights, main points, and important findings
            2. Maintain accuracy and preserve the original meaning
            3. Organize information logically with clear headings
            4. Use bullet points for key takeaways
            5. Include relevant statistics and data points when available
            6. Highlight any notable trends, patterns, or contradictions
            7. Keep the language professional yet accessible
            8. Ensure the summary is comprehensive but concise

            Format the output in markdown with the following structure:
            # [Main Topic]
            ## Key Insights
            - [Insight 1]
            - [Insight 2]
            ## Detailed Findings
            ### [Sub-topic 1]
            [Summary content]
            ### [Sub-topic 2]
            [Summary content]
            ## Conclusion
            [Overall synthesis and final thoughts]
            """
        )
        all_data = "\n".join(
            [
                f"{data.title}\n{data.href}\n{data.content}"
                for data in state.research_data
            ]
        )
        contents = [
            system_prompt,
            all_data,
        ]
        response = self.genai_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
        )
        state.summary = response.text
        return state


if __name__ == "__main__":
    # Create the Gemini client
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    # Build the graph
    graph_builder = ResearchWorkflow(genai_client=client).get_graph_builder()
    graph = graph_builder.compile()

    # Run the graph
    state = ResearchWorkflowState(
        research_topic="Please research about the Japanese economics."
    )
    # Invoke the graph asynchronously
    response = asyncio.run(graph.ainvoke(state))
    print(response)
