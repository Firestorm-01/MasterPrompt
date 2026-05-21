"""
Hacker News tool - HN Algolia API (FREE).
"""
import httpx
from tools.base import BaseTool
class HackerNewsTool(BaseTool):
    name = "hacker_news"
    description = """Search Hacker News and get top stories. FREE - no API key required.
    Actions: 'top' (limit=10), 'search' (query, limit=10)"""
    category = "Web & Research"
    required_env_vars = []
    is_free = True
    def is_available(self) -> bool:
        return True
    def _run(self, action: str = "top", query: str = None, limit: int = 10, **kwargs) -> str:
        if action == "top":
            with httpx.Client() as client:
                story_ids = client.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()[:limit]
                output = ["HN Top Stories:\n"]
                for sid in story_ids:
                    story = client.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json").json()
                    output.append(f"- [{story.get('score', 0)}] {story.get('title', 'No title')}")
            return "\n".join(output)
        elif action == "search":
            if not query:
                return "Error: 'search' requires 'query'"
            with httpx.Client() as client:
                data = client.get("https://hn.algolia.com/api/v1/search", params={"query": query, "hitsPerPage": limit}).json()
            hits = data.get("hits", [])
            return f"HN results for '{query}':\n" + "\n".join(f"- [{h.get('points', 0)}] {h.get('title', '')}" for h in hits)
        return f"Error: Unknown action '{action}'"
