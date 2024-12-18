from dify_plugin import ToolProvider
from core.tools.utils.feishu_api_utils import auth


class FeishuCalendarProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        auth(credentials)
