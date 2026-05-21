"""
Twilio SMS tool - send and receive SMS messages.
"""
import os
from typing import Optional
from tools.base import BaseTool
class TwilioSMSTool(BaseTool):
    name = "twilio_sms"
    description = """Send SMS messages via Twilio.
    Actions: 'send' (to, body), 'list' (limit=10). Phone numbers must include country code (+1234567890)"""
    category = "Communication"
    required_env_vars = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"]
    is_free = False
    def __init__(self):
        self._client = None
    def is_available(self) -> bool:
        return all([os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"), os.getenv("TWILIO_PHONE_NUMBER")])
    def _get_client(self):
        if self._client:
            return self._client
        from twilio.rest import Client
        self._client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        return self._client
    def _run(self, action: str = "send", to: Optional[str] = None, body: Optional[str] = None, limit: int = 10, **kwargs) -> str:
        client = self._get_client()
        if action == "send":
            if not all([to, body]):
                return "Error: 'send' requires 'to' and 'body'"
            message = client.messages.create(body=body, from_=os.getenv("TWILIO_PHONE_NUMBER"), to=to)
            return f"SMS sent to {to}. SID: {message.sid}"
        elif action == "list":
            messages = client.messages.list(limit=limit)
            return "Messages:\n" + "\n".join(f"- {m.from_} → {m.to}: {m.body[:80]}" for m in messages)
        return f"Error: Unknown action '{action}'"
