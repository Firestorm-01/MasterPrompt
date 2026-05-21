"""
Todoist tool - create tasks, complete, list by project.
"""
import os
from typing import Optional
from tools.base import BaseTool
class TodoistTool(BaseTool):
    name = "todoist"
    description = """Manage Todoist tasks.
    Actions: 'create' (content, project_id, due_string), 'complete' (task_id), 'list' (project_id), 'list_projects' ()"""
    category = "Productivity"
    required_env_vars = ["TODOIST_API_TOKEN"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("TODOIST_API_TOKEN"))
    def _run(self, action: str, content: str = None, task_id: str = None, project_id: str = None, due_string: str = None, **kwargs) -> str:
        from todoist_api_python import TodoistAPI
        api = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))
        if action == "create":
            if not content:
                return "Error: 'create' requires 'content'"
            task = api.add_task(content=content, project_id=project_id, due_string=due_string)
            return f"Task created: {task.content} (ID: {task.id})"
        elif action == "complete":
            if not task_id:
                return "Error: 'complete' requires 'task_id'"
            api.close_task(task_id=task_id)
            return f"Task {task_id} completed."
        elif action == "list":
            tasks = api.get_tasks(project_id=project_id) if project_id else api.get_tasks()
            return "Tasks:\n" + "\n".join(f"- [{t.id}] {t.content}" for t in tasks[:20])
        elif action == "list_projects":
            projects = api.get_projects()
            return "Projects:\n" + "\n".join(f"- {p.name} (ID: {p.id})" for p in projects)
        return f"Error: Unknown action '{action}'"
