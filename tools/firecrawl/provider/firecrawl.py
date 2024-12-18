from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider
from tools.scrape import ScrapeTool


class FirecrawlProvider(ToolProvider):
    def validate_credentials(self, credentials: dict) -> None:
        try:
            for _ in ScrapeTool.from_credentials(credentials).invoke_from_executor(
                user_id="",
                tool_parameters={
                    "url": "https://google.com",
                    "onlyIncludeTags": "title",
                },
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
