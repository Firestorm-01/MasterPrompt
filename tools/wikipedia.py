"""
Wikipedia tool - search and fetch full articles (FREE).
"""
from tools.base import BaseTool
class WikipediaTool(BaseTool):
    name = "wikipedia"
    description = """Search Wikipedia and fetch full article content. FREE - no API key required.
    Actions: 'search' (query), 'fetch' (title), 'summary' (title)"""
    category = "Web & Research"
    required_env_vars = []
    is_free = True
    def is_available(self) -> bool:
        try:
            import wikipedia
            return True
        except ImportError:
            return False
    def _run(self, action: str = "search", query: str = None, title: str = None, **kwargs) -> str:
        import wikipedia
        if action == "search":
            if not query:
                return "Error: 'search' requires 'query'"
            results = wikipedia.search(query, results=10)
            return "Wikipedia results:\n" + "\n".join(f"{i+1}. {r}" for i, r in enumerate(results))
        elif action == "summary":
            if not title:
                return "Error: 'summary' requires 'title'"
            try:
                summary = wikipedia.summary(title, sentences=5, auto_suggest=True)
                return f"Summary of '{title}':\n\n{summary}"
            except Exception as e:
                return f"Error: {str(e)}"
        elif action == "fetch":
            if not title:
                return "Error: 'fetch' requires 'title'"
            try:
                page = wikipedia.page(title, auto_suggest=True)
                return f"Title: {page.title}\nURL: {page.url}\n\n{page.content[:8000]}"
            except Exception as e:
                return f"Error: {str(e)}"
        return f"Error: Unknown action '{action}'"
