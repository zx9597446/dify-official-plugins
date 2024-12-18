from typing import Any, Generator

from duckduckgo_search import DDGS

from dify_plugin.entities.model.message import SystemPromptMessage
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool

SUMMARY_PROMPT = """
User's query: 
{query}

Here is the search engine result:
{content}

Please summarize the result in a few sentences.
"""


class DuckDuckGoSearchTool(Tool):
    """
    Tool for performing a search using DuckDuckGo search engine.
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        query = tool_parameters.get("query")
        max_results = tool_parameters.get("max_results", 5)
        require_summary = tool_parameters.get("require_summary", False)
        response = DDGS().text(query, max_results=max_results)
        if require_summary:
            results = "\n".join([res.get("body") for res in response])
            results = self.summary_results(content=results, query=query)
            yield self.create_text_message(text=results)
        for res in response:
            yield self.create_json_message(res)

    def summary_results(self, content: str, query: str) -> str:
        prompt = SUMMARY_PROMPT.format(query=query, content=content)
        summary = self.session.model.llm.invoke(
            prompt_messages=[
                SystemPromptMessage(content=prompt),
            ],
            stop=[],
        )
        return summary.message.content
