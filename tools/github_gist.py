"""
GitHub Gist tool - create and read gists.
"""
import os
from tools.base import BaseTool
class GitHubGistTool(BaseTool):
    name = "github_gist"
    description = """Create and read GitHub Gists.
    Actions: 'create' (description, files, public=False), 'get' (gist_id), 'list' ()
    files format: {"filename.py": "content..."}"""
    category = "Files & Storage"
    required_env_vars = ["GITHUB_TOKEN"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("GITHUB_TOKEN"))
    def _run(self, action: str, description: str = None, files: dict = None, public: bool = False, gist_id: str = None, **kwargs) -> str:
        from github import Github
        from github import InputFileContent
        g = Github(os.getenv("GITHUB_TOKEN"))
        user = g.get_user()
        if action == "create":
            if not files:
                return "Error: 'create' requires 'files' dict"
            gist = user.create_gist(public=public, files={k: InputFileContent(v) for k, v in files.items()}, description=description or "")
            return f"Gist created: {gist.html_url}"
        elif action == "list":
            gists = list(user.get_gists())[:20]
            return "Gists:\n" + "\n".join(f"- {g.description or 'No desc'}: {g.html_url}" for g in gists)
        return f"Error: Unknown action '{action}'"
