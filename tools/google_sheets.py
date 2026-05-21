"""
Google Sheets tool - read, write, append rows.
"""
import json
import os
from tools.base import BaseTool
class GoogleSheetsTool(BaseTool):
    name = "google_sheets"
    description = """Manage Google Sheets.
    Actions: 'read' (spreadsheet_id, range), 'write' (spreadsheet_id, range, values), 'append' (spreadsheet_id, range, values)"""
    category = "Files & Storage"
    required_env_vars = ["GOOGLE_SHEETS_CREDENTIALS_JSON", "GOOGLE_SHEETS_TOKEN_JSON"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON") and os.getenv("GOOGLE_SHEETS_TOKEN_JSON"))
    def _get_service(self):
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        creds = Credentials.from_authorized_user_info(json.loads(os.getenv("GOOGLE_SHEETS_TOKEN_JSON")))
        return build("sheets", "v4", credentials=creds)
    def _run(self, action: str, spreadsheet_id: str = None, range: str = None, values: list = None, **kwargs) -> str:
        service = self._get_service()
        if action == "read":
            if not all([spreadsheet_id, range]):
                return "Error: 'read' requires 'spreadsheet_id' and 'range'"
            result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range).execute()
            rows = result.get("values", [])
            return "Data:\n" + "\n".join(" | ".join(str(c) for c in row) for row in rows[:50])
        elif action == "write":
            if not all([spreadsheet_id, range, values]):
                return "Error: 'write' requires 'spreadsheet_id', 'range', 'values'"
            service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range, valueInputOption="USER_ENTERED", body={"values": values}).execute()
            return f"Data written to {range}"
        elif action == "append":
            if not all([spreadsheet_id, range, values]):
                return "Error: 'append' requires 'spreadsheet_id', 'range', 'values'"
            service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range, valueInputOption="USER_ENTERED", body={"values": values}).execute()
            return f"Data appended to {range}"
        return f"Error: Unknown action '{action}'"
