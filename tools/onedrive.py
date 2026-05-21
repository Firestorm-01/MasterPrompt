"""
OneDrive tool - upload/download via Microsoft Graph.
"""
import os
from tools.base import BaseTool
class OneDriveTool(BaseTool):
    name = "onedrive"
    description = """Manage OneDrive files.
    Actions: 'list' (path='/'), 'upload' (file_path, onedrive_path)"""
    category = "Files & Storage"
    required_env_vars = ["OUTLOOK_CLIENT_ID", "OUTLOOK_CLIENT_SECRET", "OUTLOOK_TENANT_ID"]
    is_free = False
    def is_available(self) -> bool:
        return all([os.getenv("OUTLOOK_CLIENT_ID"), os.getenv("OUTLOOK_CLIENT_SECRET"), os.getenv("OUTLOOK_TENANT_ID")])
    def _get_token(self) -> str:
        import msal
        app = msal.ConfidentialClientApplication(os.getenv("OUTLOOK_CLIENT_ID"), authority=f"https://login.microsoftonline.com/{os.getenv('OUTLOOK_TENANT_ID')}", client_credential=os.getenv("OUTLOOK_CLIENT_SECRET"))
        return app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])["access_token"]
    def _run(self, action: str, path: str = "/", file_path: str = None, onedrive_path: str = None, **kwargs) -> str:
        import httpx
        token = self._get_token()
        headers = {"Authorization": f"Bearer {token}"}
        base = "https://graph.microsoft.com/v1.0/me/drive"
        if action == "list":
            url = f"{base}/root/children" if path == "/" else f"{base}/root:/{path}:/children"
            with httpx.Client() as client:
                data = client.get(url, headers=headers).json()
            return "Files:\n" + "\n".join(f"- {i['name']}" for i in data.get("value", []))
        elif action == "upload":
            if not all([file_path, onedrive_path]):
                return "Error: 'upload' requires 'file_path' and 'onedrive_path'"
            with open(file_path, "rb") as f:
                content = f.read()
            with httpx.Client() as client:
                client.put(f"{base}/root:/{onedrive_path}:/content", headers={**headers, "Content-Type": "application/octet-stream"}, content=content)
            return f"Uploaded to OneDrive: {onedrive_path}"
        return f"Error: Unknown action '{action}'"
