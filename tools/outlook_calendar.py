"""
Outlook Calendar tool - create events via Microsoft Graph.
"""
import os
from tools.base import BaseTool
class OutlookCalendarTool(BaseTool):
    name = "outlook_calendar"
    description = """Manage Outlook Calendar events.
    Actions: 'create' (subject, start, end, attendees=[]), 'list' (), 'delete' (event_id)"""
    category = "Productivity"
    required_env_vars = ["OUTLOOK_CLIENT_ID", "OUTLOOK_CLIENT_SECRET", "OUTLOOK_TENANT_ID"]
    is_free = False
    def is_available(self) -> bool:
        return all([os.getenv("OUTLOOK_CLIENT_ID"), os.getenv("OUTLOOK_CLIENT_SECRET"), os.getenv("OUTLOOK_TENANT_ID")])
    def _get_token(self) -> str:
        import msal
        app = msal.ConfidentialClientApplication(os.getenv("OUTLOOK_CLIENT_ID"), authority=f"https://login.microsoftonline.com/{os.getenv('OUTLOOK_TENANT_ID')}", client_credential=os.getenv("OUTLOOK_CLIENT_SECRET"))
        return app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])["access_token"]
    def _run(self, action: str, subject: str = None, start: str = None, end: str = None, attendees: list = None, event_id: str = None, **kwargs) -> str:
        import httpx
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        base_url = "https://graph.microsoft.com/v1.0/me/events"
        if action == "create":
            if not all([subject, start, end]):
                return "Error: 'create' requires 'subject', 'start', 'end'"
            event = {"subject": subject, "start": {"dateTime": start, "timeZone": "UTC"}, "end": {"dateTime": end, "timeZone": "UTC"}, "attendees": [{"emailAddress": {"address": a}} for a in (attendees or [])]}
            with httpx.Client() as client:
                data = client.post(base_url, headers=headers, json=event).json()
            return f"Event created: {data['subject']}"
        elif action == "list":
            with httpx.Client() as client:
                data = client.get(f"{base_url}?$top=20", headers=headers).json()
            return "Events:\n" + "\n".join(f"- {e['subject']}: {e['start']['dateTime']}" for e in data.get("value", []))
        return f"Error: Unknown action '{action}'"
