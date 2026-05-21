"""
Jira tool - create/update tickets, search, transition.
"""
import os
from typing import Optional
from tools.base import BaseTool
class JiraTool(BaseTool):
    name = "jira"
    description = """Manage Jira issues.
    Actions: 'create' (project, summary, description, issue_type='Task'), 'update' (issue_key, fields={}),
    'transition' (issue_key, transition_name), 'search' (jql), 'get' (issue_key), 'comment' (issue_key, body)"""
    category = "Productivity"
    required_env_vars = ["JIRA_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"]
    is_free = False
    def __init__(self):
        self._jira = None
    def is_available(self) -> bool:
        return all([os.getenv("JIRA_URL"), os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN")])
    def _get_jira(self):
        if self._jira:
            return self._jira
        from jira import JIRA
        self._jira = JIRA(server=os.getenv("JIRA_URL"), basic_auth=(os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN")))
        return self._jira
    def _run(self, action: str, project: Optional[str] = None, summary: Optional[str] = None,
             description: Optional[str] = None, issue_type: str = "Task", issue_key: Optional[str] = None,
             fields: dict = None, transition_name: Optional[str] = None, jql: Optional[str] = None,
             body: Optional[str] = None, **kwargs) -> str:
        jira = self._get_jira()
        if action == "create":
            if not all([project, summary]):
                return "Error: 'create' requires 'project' and 'summary'"
            issue = jira.create_issue(project=project, summary=summary, description=description or "", issuetype={"name": issue_type})
            base_url = os.getenv("JIRA_URL").rstrip("/")
            return f"Issue {issue.key} created: {base_url}/browse/{issue.key}"
        elif action == "search":
            if not jql:
                return "Error: 'search' requires 'jql'"
            issues = jira.search_issues(jql, maxResults=20)
            return "Issues:\n" + "\n".join(f"- {i.key}: {i.fields.summary}" for i in issues)
        elif action == "get":
            if not issue_key:
                return "Error: 'get' requires 'issue_key'"
            issue = jira.issue(issue_key)
            return f"{issue.key}: {issue.fields.summary}\nStatus: {issue.fields.status.name}"
        return f"Error: Unknown action '{action}'"
