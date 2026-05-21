"""
Slack tool - post messages, read channels, list members.
"""
import os
from typing import Optional
from tools.base import BaseTool
class SlackTool(BaseTool):
    name = "slack"
    description = """Post messages to Slack channels, read channel history, and list members.
    Actions: 'post' (channel, message), 'read' (channel, limit=10), 'list_members' (channel)."""
    category = "Communication"
    required_env_vars = ["SLACK_BOT_TOKEN"]
    is_free = False
    def __init__(self):
        self._client = None
    def is_available(self) -> bool:
        return bool(os.getenv("SLACK_BOT_TOKEN"))
    def _get_client(self):
        if self._client:
            return self._client
        from slack_sdk import WebClient
        self._client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))
        return self._client
    def _run(self, action: str, channel: Optional[str] = None, message: Optional[str] = None, limit: int = 10, **kwargs) -> str:
        client = self._get_client()
        if action == "post":
            if not all([channel, message]):
                return "Error: 'post' requires 'channel' and 'message' parameters"
            result = client.chat_postMessage(channel=channel, text=message)
            return f"Message posted to {channel} successfully."
        elif action == "read":
            if not channel:
                return "Error: 'read' requires 'channel' parameter"
            result = client.conversations_history(channel=channel, limit=limit)
            messages = result.get("messages", [])
            return f"Last {len(messages)} messages in {channel}"
        return f"Error: Unknown action '{action}'"
