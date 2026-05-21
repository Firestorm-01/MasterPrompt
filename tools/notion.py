"""
Notion tool - create, read, update pages and databases.
"""
import os
from typing import Optional
from tools.base import BaseTool
class NotionTool(BaseTool):
    name = "notion"
    description = """Manage Notion pages and databases.
    Actions: 'create_page' (parent_id, title, content), 'read_page' (page_id),
    'update_page' (page_id, content), 'search' (query), 'list_databases' ()"""
    category = "Communication"
    required_env_vars = ["NOTION_API_KEY"]
    is_free = False
    def __init__(self):
        self._client = None
    def is_available(self) -> bool:
        return bool(os.getenv("NOTION_API_KEY"))
    def _get_client(self):
        if self._client:
            return self._client
        from notion_client import Client
        self._client = Client(auth=os.getenv("NOTION_API_KEY"))
        return self._client
    def _run(self, action: str, parent_id: Optional[str] = None, page_id: Optional[str] = None,
             title: Optional[str] = None, content: Optional[str] = None, query: Optional[str] = None, **kwargs) -> str:
        client = self._get_client()
        if action == "create_page":
            if not all([parent_id, title]):
                return "Error: 'create_page' requires 'parent_id' and 'title'"
            children = [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": content[:2000]}}]}}] if content else []
            page = client.pages.create(
                parent={"page_id": parent_id},
                properties={"title": {"title": [{"text": {"content": title}}]}},
                children=children
            )
            return f"Page created: {title}\nID: {page['id']}\nURL: {page['url']}"
        elif action == "search":
            if not query:
                return "Error: 'search' requires 'query'"
            results = client.search(query=query, page_size=10)
            pages = results.get("results", [])
            if not pages:
                return f"No pages found for '{query}'"
            return f"Found {len(pages)} results for '{query}'"
        return f"Error: Unknown action '{action}'"
