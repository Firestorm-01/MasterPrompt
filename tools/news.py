"""
NewsAPI tool - headlines and search.
"""
import os
from tools.base import BaseTool
class NewsAPITool(BaseTool):
    name = "news_api"
    description = """Get news headlines and search articles.
    Actions: 'headlines' (country='us', category), 'search' (query)"""
    category = "Web & Research"
    required_env_vars = ["NEWS_API_KEY"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("NEWS_API_KEY"))
    def _run(self, action: str = "headlines", query: str = None, country: str = "us", category: str = None, **kwargs) -> str:
        from newsapi import NewsApiClient
        api = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
        if action == "headlines":
            params = {"country": country}
            if category:
                params["category"] = category
            data = api.get_top_headlines(**params)
        elif action == "search":
            if not query:
                return "Error: 'search' requires 'query'"
            data = api.get_everything(q=query)
        else:
            return f"Error: Unknown action '{action}'"
        articles = data.get("articles", [])[:10]
        return "Articles:\n" + "\n".join(f"- {a['title']} ({a['source']['name']})\n  {a['url']}" for a in articles)
