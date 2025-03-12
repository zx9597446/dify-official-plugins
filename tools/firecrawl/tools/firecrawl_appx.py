# Add this method to the FirecrawlApp class in firecrawl_appx.py

def search(self, payload: dict):
    """
    Search the web and get content from search results.
    
    Args:
        payload (dict): A dictionary containing search parameters:
            - query (str): The search query (required)
            - limit (int, optional): Maximum number of results to return (default: 5)
            - tbs (str, optional): Time-based search parameter
            - lang (str, optional): Language code for search results (default: en)
            - country (str, optional): Country code for search results (default: us)
            - location (str, optional): Location parameter for search results
            - timeout (int, optional): Timeout in milliseconds (default: 60000)
            - scrapeOptions (dict, optional): Options for scraping search results
                - formats (list, optional): Formats to include in the output
    
    Returns:
        dict: The search results
    """
    endpoint = f"{self.base_url}/search"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.api_key}"
    }
    
    response = self._make_request("POST", endpoint, headers=headers, json=payload)
    return response