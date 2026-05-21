"""
WhatsApp tool - send messages via Twilio WhatsApp sandbox.
"""
import os
from tools.base import BaseTool
class WhatsAppTool(BaseTool):
    name = "whatsapp"
    description = """Send WhatsApp messages via Twilio WhatsApp sandbox.
    Parameters: to (phone number with country code), message (text content)"""
    category = "Communication"
    required_env_vars = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER"]
    is_free = False
    def is_available(self) -> bool:
        return all([os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"), os.getenv("TWILIO_PHONE_NUMBER")])
    def _run(self, to: str, message: str, **kwargs) -> str:
        from twilio.rest import Client
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        msg = client.messages.create(body=message, from_=f"whatsapp:{os.getenv('TWILIO_PHONE_NUMBER')}", to=f"whatsapp:{to}")
        return f"WhatsApp message sent to {to}. SID: {msg.sid}"
