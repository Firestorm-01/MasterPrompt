"""
Google Docs tool - create, read, append documents.
"""
import json
import os
from tools.base import BaseTool
class GoogleDocsTool(BaseTool):
    name = "google_docs"
    description = """Manage Google Docs.
    Actions: 'create' (title, content), 'read' (document_id), 'append' (document_id, content)"""
    category = "Files & Storage"
    required_env_vars = ["GOOGLE_DOCS_CREDENTIALS_JSON", "GOOGLE_DOCS_TOKEN_JSON"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("GOOGLE_DOCS_CREDENTIALS_JSON") and os.getenv("GOOGLE_DOCS_TOKEN_JSON"))
    def _get_services(self):
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        creds = Credentials.from_authorized_user_info(json.loads(os.getenv("GOOGLE_DOCS_TOKEN_JSON")))
        return build("docs", "v1", credentials=creds), build("drive", "v3", credentials=creds)
    def _run(self, action: str, title: str = None, content: str = None, document_id: str = None, **kwargs) -> str:
        docs, drive = self._get_services()
        if action == "create":
            if not title:
                return "Error: 'create' requires 'title'"
            doc = docs.documents().create(body={"title": title}).execute()
            doc_id = doc["documentId"]
            if content:
                docs.documents().batchUpdate(documentId=doc_id, body={"requests": [{"insertText": {"location": {"index": 1}, "text": content}}]}).execute()
            return f"Document created: {title}\nID: {doc_id}\nURL: https://docs.google.com/document/d/{doc_id}"
        elif action == "read":
            if not document_id:
                return "Error: 'read' requires 'document_id'"
            doc = docs.documents().get(documentId=document_id).execute()
            text = ""
            for elem in doc.get("body", {}).get("content", []):
                if "paragraph" in elem:
                    for el in elem["paragraph"].get("elements", []):
                        if "textRun" in el:
                            text += el["textRun"]["content"]
            return f"Title: {doc['title']}\n\n{text[:5000]}"
        return f"Error: Unknown action '{action}'"
