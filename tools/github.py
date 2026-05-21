"""
GitHub tool - create repos, open PRs, create issues, search code.
"""
import os
from typing import Optional
from tools.base import BaseTool
class GitHubTool(BaseTool):
    name = "github"
    description = """Interact with GitHub repositories.
    Actions: 'create_repo' (name, description, private=False), 'create_issue' (repo, title, body),
    'create_pr' (repo, title, body, head, base='main'), 'search_code' (query), 'list_issues' (repo, state='open'), 'get_repo' (repo)"""
    category = "Productivity"
    required_env_vars = ["GITHUB_TOKEN"]
    is_free = False
    def __init__(self):
        self._github = None
    def is_available(self) -> bool:
        return bool(os.getenv("GITHUB_TOKEN"))
    def _get_github(self):
        if self._github:
            return self._github
        from github import Github
        self._github = Github(os.getenv("GITHUB_TOKEN"))
        return self._github
    def _run(self, action: str, repo: Optional[str] = None, name: Optional[str] = None,
             title: Optional[str] = None, body: Optional[str] = None, description: Optional[str] = None,
             private: bool = False, labels: list = None, head: Optional[str] = None,
             base: str = "main", query: Optional[str] = None, state: str = "open", **kwargs) -> str:
        g = self._get_github()
        if action == "create_issue":
            if not all([repo, title]):
                return "Error: 'create_issue' requires 'repo' and 'title'"
            repository = g.get_repo(repo)
            issue = repository.create_issue(title=title, body=body or "")
            return f"Issue #{issue.number} created: {issue.html_url}"
        elif action == "list_issues":
            if not repo:
                return "Error: 'list_issues' requires 'repo'"
            repository = g.get_repo(repo)
            issues = list(repository.get_issues(state=state))[:20]
            if not issues:
                return f"No {state} issues in {repo}"
            return "Issues:\n" + "\n".join(f"- #{i.number}: {i.title}" for i in issues)
        elif action == "get_repo":
            if not repo:
                return "Error: 'get_repo' requires 'repo'"
            r = g.get_repo(repo)
            return f"Repo: {r.full_name}\nStars: {r.stargazers_count}\nURL: {r.html_url}"
        return f"Error: Unknown action '{action}'"
