"""
Outlook tool - email via Microsoft Graph API.
"""
import os
from tools.base import BaseTool
class OutlookTool(BaseTool):
    name = "outlook"
    description = """Send and read Outlook emails via Microsoft Graph.
    Actions: 'send' (to, subject, body), 'list' (limit=10)"""
    category = "Communication"
    required_env_vars = ["OUTLOOK_CLIENT_ID", "OUTLOOK_CLIENT_SECRET", "OUTLOOK_TENANT_ID"]
    is_free = False
    def is_available(self) -> bool:
        return all([os.getenv("OUTLOOK_CLIENT_ID"), os.getenv("OUTLOOK_CLIENT_SECRET"), os.getenv("OUTLOOK_TENANT_ID")])
    def _get_token(self) -> str:
        import msal
        app = msal.ConfidentialClientApplication(
            os.getenv("OUTLOOK_CLIENT_ID"),
            authority=f"https://login.microsoftonline.com/{os.getenv('OUTLOOK_TENANT_ID')}",
            client_credential=os.getenv("OUTLOOK_CLIENT_SECRET")
        )
        return app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])["access_token"]
    def _run(self, action: str, to: str = None, subject: str = None, body: str = None, limit: int = 10, **kwargs) -> str:
        import httpx
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        base_url = "https://graph.microsoft.com/v1.0/me"
        if action == "send":
            if not all([to, subject, body]):
                return "Error: 'send' requires 'to', 'subject', and 'body'"
            payload = {"message": {"subject": subject, "body": {"contentType": "Text", "content": body}, "toRecipients": [{"emailAddress": {"address": to}}]}}
            with httpx.Client() as client:
                client.post(f"{base_url}/sendMail", headers=headers, json=payload).raise_for_status()
            return f"Email sent to {to}"
        elif action == "list":
            with httpx.Client() as client:
                data = client.get(f"{base_url}/messages?$top={limit}", headers=headers).json()
            return "Emails:\n" + "\n".join(f"- {m['subject']} (from {m['from']['emailAddress']['address']})" for m in data.get("value", []))
        return f"Error: Unknown action '{action}'"
