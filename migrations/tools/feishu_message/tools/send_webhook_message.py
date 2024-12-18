from typing import Any
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from core.tools.utils.feishu_api_utils import FeishuRequest


class SendWebhookMessageTool(Tool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> ToolInvokeMessage:
        app_id = self.runtime.credentials.get("app_id")
        app_secret = self.runtime.credentials.get("app_secret")
        client = FeishuRequest(app_id, app_secret)
        webhook = tool_parameters.get("webhook")
        msg_type = tool_parameters.get("msg_type")
        content = tool_parameters.get("content")
        res = client.send_webhook_message(webhook, msg_type, content)
        return self.create_json_message(res)
