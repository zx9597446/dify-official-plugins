from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.aippt import AIPPTGenerateTool
from dify_plugin import ToolProvider


class AIPPTProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        try:
            AIPPTGenerateTool._get_api_token(credentials, user_id="__dify_system__")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
