"""
Webhook tool - fire arbitrary POST webhooks.
"""
import httpx
from tools.base import BaseTool
class WebhookTool(BaseTool):
    name = "webhook"
    description = """Send POST requests to webhooks.
    Parameters: url (webhook URL), payload (JSON dict), headers (optional dict)"""
    category = "AI & Dev"
    required_env_vars = []
    is_free = True
    def is_available(self) -> bool:
        return True
    def _run(self, url: str, payload: dict = None, headers: dict = None, **kwargs) -> str:
        if not url:
            return "Error: 'url' is required"
        default_headers = {"Content-Type": "application/json"}
        if headers:
            default_headers.update(headers)
        with httpx.Client() as client:
            response = client.post(url, json=payload or {}, headers=default_headers, timeout=30.0)
        return f"Webhook sent to {url}\nStatus: {response.status_code}\nResponse: {response.text[:500]}"
