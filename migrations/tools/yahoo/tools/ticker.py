from typing import Any, Union
from requests.exceptions import HTTPError, ReadTimeout
from yfinance import Ticker
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class YahooFinanceSearchTickerTool(Tool):
    def _invoke(
        self, user_id: str, tool_parameters: dict[str, Any]
    ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
        invoke tools
        """
        query = tool_parameters.get("symbol", "")
        if not query:
            return self.create_text_message("Please input symbol")
        try:
            return self.create_text_message(self.run(ticker=query))
        except (HTTPError, ReadTimeout):
            return self.create_text_message("There is a internet connection problem. Please try again later.")

    def run(self, ticker: str) -> str:
        return str(Ticker(ticker).info)
