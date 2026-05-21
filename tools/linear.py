"""
Linear tool - create issues, update status via GraphQL API.
"""
import os
from tools.base import BaseTool
class LinearTool(BaseTool):
    name = "linear"
    description = """Manage Linear issues.
    Actions: 'create' (title, description, team_id), 'search' (query), 'list_teams' ()"""
    category = "Productivity"
    required_env_vars = ["LINEAR_API_KEY"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("LINEAR_API_KEY"))
    def _run(self, action: str, title: str = None, description: str = None, team_id: str = None, query: str = None, **kwargs) -> str:
        import httpx
        headers = {"Authorization": os.getenv("LINEAR_API_KEY"), "Content-Type": "application/json"}
        url = "https://api.linear.app/graphql"
        if action == "create":
            if not all([title, team_id]):
                return "Error: 'create' requires 'title' and 'team_id'"
            gql = """mutation($title: String!, $teamId: String!, $description: String) {
                issueCreate(input: {title: $title, teamId: $teamId, description: $description}) {
                    issue { id identifier title url } } }"""
            with httpx.Client() as client:
                resp = client.post(url, headers=headers, json={"query": gql, "variables": {"title": title, "teamId": team_id, "description": description}})
                issue = resp.json()["data"]["issueCreate"]["issue"]
            return f"Issue created: {issue['identifier']} - {issue['title']}\nURL: {issue['url']}"
        elif action == "list_teams":
            gql = "query { teams { nodes { id name key } } }"
            with httpx.Client() as client:
                resp = client.post(url, headers=headers, json={"query": gql})
                teams = resp.json()["data"]["teams"]["nodes"]
            return "Teams:\n" + "\n".join(f"- {t['name']} (ID: {t['id']})" for t in teams)
        return f"Error: Unknown action '{action}'"
