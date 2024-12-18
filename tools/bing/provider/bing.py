from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.bing_web_search import BingWebSearchTool


class BingProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in BingWebSearchTool.from_credentials(credentials).invoke(
                tool_parameters={
                    "query": "test",
                    "enable_computation": True,
                    "enable_entities": True,
                    "enable_news": True,
                    "enable_related_search": True,
                    "enable_webpages": True,
                    "limit": 10,
                    "result_type": "link",
                    "market": "US",
                    "language": "en",
                },
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
