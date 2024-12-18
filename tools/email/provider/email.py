from tools.send_mail import SendMailTool
from dify_plugin import ToolProvider


class SmtpProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        SendMailTool()
