"""
Zoom tool - create meetings and get join URLs.
"""
import os
from typing import Optional
from tools.base import BaseTool
class ZoomTool(BaseTool):
    name = "zoom"
    description = """Create and manage Zoom meetings.
    Actions: 'create' (topic, duration=60, start_time, agenda=''), 'list' (), 'get' (meeting_id), 'delete' (meeting_id)"""
    category = "Communication"
    required_env_vars = ["ZOOM_CLIENT_ID", "ZOOM_CLIENT_SECRET", "ZOOM_ACCOUNT_ID"]
    is_free = False
    def __init__(self):
        self._token = None
    def is_available(self) -> bool:
        return all([os.getenv("ZOOM_CLIENT_ID"), os.getenv("ZOOM_CLIENT_SECRET"), os.getenv("ZOOM_ACCOUNT_ID")])
    def _get_token(self) -> str:
        if self._token:
            return self._token
        import httpx, base64
        credentials = base64.b64encode(f"{os.getenv('ZOOM_CLIENT_ID')}:{os.getenv('ZOOM_CLIENT_SECRET')}".encode()).decode()
        with httpx.Client() as client:
            response = client.post("https://zoom.us/oauth/token", headers={"Authorization": f"Basic {credentials}"}, data={"grant_type": "account_credentials", "account_id": os.getenv("ZOOM_ACCOUNT_ID")})
            self._token = response.json()["access_token"]
        return self._token
    def _run(self, action: str, topic: Optional[str] = None, duration: int = 60, start_time: Optional[str] = None, agenda: str = "", meeting_id: Optional[str] = None, **kwargs) -> str:
        import httpx
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        if action == "create":
            if not topic:
                return "Error: 'create' requires 'topic'"
            payload = {"topic": topic, "type": 2 if start_time else 1, "duration": duration, "agenda": agenda}
            if start_time:
                payload["start_time"] = start_time
            with httpx.Client() as client:
                resp = client.post("https://api.zoom.us/v2/users/me/meetings", headers=headers, json=payload)
                data = resp.json()
            return f"Meeting created: {data['topic']}\nJoin URL: {data['join_url']}\nPassword: {data.get('password', 'None')}"
        elif action == "list":
            with httpx.Client() as client:
                resp = client.get("https://api.zoom.us/v2/users/me/meetings", headers=headers)
                data = resp.json()
            meetings = data.get("meetings", [])
            return "Meetings:\n" + "\n".join(f"- {m['topic']}: {m['join_url']}" for m in meetings)
        return f"Error: Unknown action '{action}'"
