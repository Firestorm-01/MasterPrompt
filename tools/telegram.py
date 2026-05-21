"""
Telegram tool - send messages via bot.
"""
import os
from tools.base import BaseTool
class TelegramTool(BaseTool):
    name = "telegram"
    description = """Send messages via Telegram bot.
    Parameters: chat_id (required), message (required), parse_mode (optional: 'HTML' or 'Markdown')"""
    category = "Communication"
    required_env_vars = ["TELEGRAM_BOT_TOKEN"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("TELEGRAM_BOT_TOKEN"))
    def _run(self, chat_id: str, message: str, parse_mode: str = None, **kwargs) -> str:
        import httpx
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        payload = {"chat_id": chat_id, "text": message}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        with httpx.Client() as client:
            response = client.post(f"https://api.telegram.org/bot{token}/sendMessage", json=payload)
            response.raise_for_status()
        return f"Message sent to Telegram chat {chat_id}"
