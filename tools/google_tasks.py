"""
Google Tasks tool - create and complete tasks.
"""
import json
import os
from tools.base import BaseTool
class GoogleTasksTool(BaseTool):
    name = "google_tasks"
    description = """Manage Google Tasks.
    Actions: 'list_tasklists' (), 'list' (tasklist_id), 'create' (tasklist_id, title, notes, due), 'complete' (tasklist_id, task_id)"""
    category = "Productivity"
    required_env_vars = ["GOOGLE_TASKS_CREDENTIALS_JSON", "GOOGLE_TASKS_TOKEN_JSON"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("GOOGLE_TASKS_CREDENTIALS_JSON") and os.getenv("GOOGLE_TASKS_TOKEN_JSON"))
    def _get_service(self):
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        creds = Credentials.from_authorized_user_info(json.loads(os.getenv("GOOGLE_TASKS_TOKEN_JSON")))
        return build("tasks", "v1", credentials=creds)
    def _run(self, action: str, tasklist_id: str = None, task_id: str = None, title: str = None, notes: str = None, due: str = None, **kwargs) -> str:
        service = self._get_service()
        if action == "list_tasklists":
            items = service.tasklists().list().execute().get("items", [])
            return "Task Lists:\n" + "\n".join(f"- {t['title']} (ID: {t['id']})" for t in items)
        elif action == "list":
            if not tasklist_id:
                return "Error: 'list' requires 'tasklist_id'"
            items = service.tasks().list(tasklist=tasklist_id).execute().get("items", [])
            return "Tasks:\n" + "\n".join(f"- {t['title']}" for t in items)
        elif action == "create":
            if not all([tasklist_id, title]):
                return "Error: 'create' requires 'tasklist_id' and 'title'"
            task = {"title": title}
            if notes:
                task["notes"] = notes
            result = service.tasks().insert(tasklist=tasklist_id, body=task).execute()
            return f"Task created: {result['title']}"
        return f"Error: Unknown action '{action}'"
