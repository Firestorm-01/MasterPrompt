"""
Google Drive tool - upload, download, search, share files.
"""
import json
import os
from tools.base import BaseTool
class GoogleDriveTool(BaseTool):
    name = "google_drive"
    description = """Manage Google Drive files.
    Actions: 'list' (), 'search' (query), 'share' (file_id, email, role='reader')"""
    category = "Files & Storage"
    required_env_vars = ["GOOGLE_DRIVE_CREDENTIALS_JSON", "GOOGLE_DRIVE_TOKEN_JSON"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("GOOGLE_DRIVE_CREDENTIALS_JSON") and os.getenv("GOOGLE_DRIVE_TOKEN_JSON"))
    def _get_service(self):
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        creds = Credentials.from_authorized_user_info(json.loads(os.getenv("GOOGLE_DRIVE_TOKEN_JSON")))
        return build("drive", "v3", credentials=creds)
    def _run(self, action: str, query: str = None, file_id: str = None, email: str = None, role: str = "reader", **kwargs) -> str:
        service = self._get_service()
        if action == "list":
            results = service.files().list(pageSize=20, fields="files(id, name, mimeType)").execute()
            files = results.get("files", [])
            return "Files:\n" + "\n".join(f"- {f['name']} ({f['id'][:10]}...)" for f in files)
        elif action == "search":
            if not query:
                return "Error: 'search' requires 'query'"
            results = service.files().list(q=f"name contains '{query}'", pageSize=20, fields="files(id, name)").execute()
            files = results.get("files", [])
            return "Files:\n" + "\n".join(f"- {f['name']} ({f['id']})" for f in files)
        elif action == "share":
            if not all([file_id, email]):
                return "Error: 'share' requires 'file_id' and 'email'"
            service.permissions().create(fileId=file_id, body={"type": "user", "role": role, "emailAddress": email}).execute()
            return f"File {file_id} shared with {email}"
        return f"Error: Unknown action '{action}'"
