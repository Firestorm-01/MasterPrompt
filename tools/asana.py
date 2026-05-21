"""
Asana tool - create tasks, assign, set due dates.
"""
import os
from tools.base import BaseTool
class AsanaTool(BaseTool):
    name = "asana"
    description = """Manage Asana tasks.
    Actions: 'create' (name, project_gid, notes, due_on), 'complete' (task_gid), 'list' (project_gid), 'list_projects' (workspace_gid)"""
    category = "Productivity"
    required_env_vars = ["ASANA_ACCESS_TOKEN"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("ASANA_ACCESS_TOKEN"))
    def _run(self, action: str, name: str = None, project_gid: str = None, task_gid: str = None, notes: str = None, due_on: str = None, workspace_gid: str = None, **kwargs) -> str:
        import asana
        client = asana.Client.access_token(os.getenv("ASANA_ACCESS_TOKEN"))
        if action == "create":
            if not all([name, project_gid]):
                return "Error: 'create' requires 'name' and 'project_gid'"
            task_data = {"name": name, "projects": [project_gid]}
            if notes:
                task_data["notes"] = notes
            if due_on:
                task_data["due_on"] = due_on
            task = client.tasks.create_task(task_data)
            return f"Task created: {task['name']} (GID: {task['gid']})"
        elif action == "complete":
            if not task_gid:
                return "Error: 'complete' requires 'task_gid'"
            client.tasks.update_task(task_gid, {"completed": True})
            return f"Task {task_gid} marked complete."
        elif action == "list":
            if not project_gid:
                return "Error: 'list' requires 'project_gid'"
            tasks = list(client.tasks.get_tasks_for_project(project_gid))
            return "Tasks:\n" + "\n".join(f"- {t['name']}" for t in tasks[:20])
        return f"Error: Unknown action '{action}'"
