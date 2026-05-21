"""
Discord tool - send messages to channels or DMs.
"""
import os
from tools.base import BaseTool
class DiscordTool(BaseTool):
    name = "discord"
    description = """Send messages to Discord channels via bot.
    Parameters: channel_id (required), message (required), embed (optional dict)"""
    category = "Communication"
    required_env_vars = ["DISCORD_BOT_TOKEN"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("DISCORD_BOT_TOKEN"))
    def _run(self, channel_id: str, message: str, embed: dict = None, **kwargs) -> str:
        import httpx
        token = os.getenv("DISCORD_BOT_TOKEN")
        headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}
        payload = {"content": message}
        if embed:
            payload["embeds"] = [embed]
        with httpx.Client() as client:
            response = client.post(f"https://discord.com/api/v10/channels/{channel_id}/messages", headers=headers, json=payload)
            response.raise_for_status()
        return f"Message sent to Discord channel {channel_id}"
