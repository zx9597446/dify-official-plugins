from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.tavily_search import TavilySearchTool
from dify_plugin import ToolProvider


class TavilyProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            TavilySearchTool.from_credentials(credentials, user_id="").invoke(
                tool_parameters={
                    "query": "Sachin Tendulkar",
                    "search_depth": "basic",
                    "include_answer": True,
                    "include_images": False,
                    "include_raw_content": False,
                    "max_results": 5,
                    "include_domains": "",
                    "exclude_domains": "",
                }
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
