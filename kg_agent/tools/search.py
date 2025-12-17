from tavily import TavilyClient
from app.config import settings

class SearchTool:
    def __init__(self):
        self.client = None
        if settings.TAVILY_API_KEY:
            self.client = TavilyClient(api_key=settings.TAVILY_API_KEY)

    def search(self, query: str, max_results: int = 5):
        if not self.client:
            return []
        
        try:
            response = self.client.search(query, max_results=max_results)
            return response.get("results", [])
        except Exception as e:
            print(f"Search error: {e}")
            return []
