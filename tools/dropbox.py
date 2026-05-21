"""
Dropbox tool - upload, download, list files.
"""
import os
from tools.base import BaseTool
class DropboxTool(BaseTool):
    name = "dropbox"
    description = """Manage Dropbox files.
    Actions: 'list' (path='/'), 'upload' (file_path, dropbox_path), 'download' (dropbox_path)"""
    category = "Files & Storage"
    required_env_vars = ["DROPBOX_ACCESS_TOKEN"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("DROPBOX_ACCESS_TOKEN"))
    def _run(self, action: str, path: str = "/", file_path: str = None, dropbox_path: str = None, **kwargs) -> str:
        import dropbox
        dbx = dropbox.Dropbox(os.getenv("DROPBOX_ACCESS_TOKEN"))
        if action == "list":
            result = dbx.files_list_folder(path if path != "/" else "")
            return "Files:\n" + "\n".join(f"- {e.name}" for e in result.entries)
        elif action == "upload":
            if not all([file_path, dropbox_path]):
                return "Error: 'upload' requires 'file_path' and 'dropbox_path'"
            with open(file_path, "rb") as f:
                dbx.files_upload(f.read(), dropbox_path)
            return f"Uploaded to {dropbox_path}"
        elif action == "download":
            if not dropbox_path:
                return "Error: 'download' requires 'dropbox_path'"
            metadata, response = dbx.files_download(dropbox_path)
            local_path = f"/tmp/{metadata.name}"
            with open(local_path, "wb") as f:
                f.write(response.content)
            return f"Downloaded to {local_path}"
        return f"Error: Unknown action '{action}'"
