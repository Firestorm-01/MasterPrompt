"""
Web search tool using Tavily API.
"""
import os
from tools.base import BaseTool
class WebSearchTool(BaseTool):
    name = "web_search"
    description = """Search the web using Tavily API. Returns top 5 results with titles, URLs, and content snippets.
    Parameters: query (required), max_results (optional, default 5)"""
    category = "Web & Research"
    required_env_vars = ["TAVILY_API_KEY"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("TAVILY_API_KEY"))
    def _run(self, query: str, max_results: int = 5, **kwargs) -> str:
        from tavily import TavilyClient
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        response = client.search(query=query, max_results=max_results, include_answer=True)
        output = []
        if response.get("answer"):
            output.append(f"Summary: {response['answer']}\n")
        output.append(f"Top results for '{query}':\n")
        for i, result in enumerate(response.get("results", []), 1):
            output.append(f"{i}. {result.get('title', 'No title')}")
            output.append(f"   URL: {result.get('url', '')}")
            output.append(f"   {result.get('content', '')[:300]}...\n")
        return "\n".join(output)
