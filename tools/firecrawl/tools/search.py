from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from .firecrawl_appx import FirecrawlApp, get_array_params, get_json_params


class SearchTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        the api doc:
        https://docs.firecrawl.dev/api-reference/endpoint/search
        """
        app = FirecrawlApp(
            api_key=self.runtime.credentials["firecrawl_api_key"],
            base_url=self.runtime.credentials["base_url"],
        )
        payload = {}
        scrape_options = {}

        # Required parameter
        payload["query"] = tool_parameters["query"]

        # Optional parameters with defaults
        payload["limit"] = tool_parameters.get("limit", 5)
        payload["lang"] = tool_parameters.get("lang", "en")
        payload["country"] = tool_parameters.get("country", "us")
        payload["timeout"] = tool_parameters.get("timeout", 60000)

        # Optional parameters without defaults
        if "tbs" in tool_parameters:
            payload["tbs"] = tool_parameters["tbs"]
        if "location" in tool_parameters:
            payload["location"] = tool_parameters["location"]

        # Scrape options
        scrape_options["formats"] = get_array_params(tool_parameters, "formats")
        if scrape_options["formats"]:
            payload["scrapeOptions"] = scrape_options

        # Filter out None and empty values
        payload = {k: v for (k, v) in payload.items() if v not in (None, "")}

        # Call search API
        search_result = app.search(payload=payload)

        # Return the search results
        yield self.create_text_message(
            f"Search results for: {tool_parameters['query']}"
        )
        yield self.create_json_message(search_result)
