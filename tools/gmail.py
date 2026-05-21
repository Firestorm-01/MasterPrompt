"""
Gmail tool - send, read, search, and reply to emails via Gmail API.
"""
import base64
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from tools.base import BaseTool


class GmailTool(BaseTool):
    name = "gmail"
    description = """Send, read, search, and reply to Gmail messages.
    Actions: 'send' (to, subject, body), 'read' (message_id), 'search' (query), 'reply' (message_id, body).
    Search uses Gmail query syntax (e.g., 'is:unread from:example@gmail.com')."""
    category = "Communication"
    required_env_vars = ["GMAIL_CREDENTIALS_JSON", "GMAIL_TOKEN_JSON"]
    is_free = False

    def __init__(self):
        self._service = None

    def is_available(self) -> bool:
        return bool(os.getenv("GMAIL_CREDENTIALS_JSON") and os.getenv("GMAIL_TOKEN_JSON"))

    def _get_service(self):
        if self._service:
            return self._service
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        token_data = json.loads(os.getenv("GMAIL_TOKEN_JSON"))
        creds = Credentials.from_authorized_user_info(token_data)
        self._service = build("gmail", "v1", credentials=creds)
        return self._service

    def _run(
        self,
        action: str,
        to: Optional[str] = None,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        query: Optional[str] = None,
        message_id: Optional[str] = None,
        **kwargs
    ) -> str:
        service = self._get_service()

        if action == "send":
            if not all([to, subject, body]):
                return "Error: 'send' requires 'to', 'subject', and 'body'"
            return self._send_email(service, to, subject, body)

        elif action == "read":
            if not message_id:
                return "Error: 'read' requires 'message_id'"
            return self._read_email(service, message_id)

        elif action == "search":
            if not query:
                return "Error: 'search' requires 'query'"
            return self._search_emails(service, query)

        elif action == "reply":
            if not all([message_id, body]):
                return "Error: 'reply' requires 'message_id' and 'body'"
            return self._reply_email(service, message_id, body)

        return f"Error: Unknown action '{action}'. Use: send, read, search, or reply"

    def _send_email(self, service, to: str, subject: str, body: str) -> str:
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        result = service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return f"Email sent successfully. Message ID: {result['id']}"

    def _read_email(self, service, message_id: str) -> str:
        msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
        body = ""
        if "parts" in msg["payload"]:
            for part in msg["payload"]["parts"]:
                if part["mimeType"] == "text/plain" and "data" in part.get("body", {}):
                    body = base64.urlsafe_b64decode(part["body"]["data"]).decode()
                    break
        elif "body" in msg["payload"] and "data" in msg["payload"]["body"]:
            body = base64.urlsafe_b64decode(msg["payload"]["body"]["data"]).decode()
        return f"From: {headers.get('From', 'Unknown')}\nSubject: {headers.get('Subject', 'No subject')}\nDate: {headers.get('Date', 'Unknown')}\n\n{body[:2000]}"

    def _search_emails(self, service, query: str, max_results: int = 10) -> str:
        results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        messages = results.get("messages", [])
        if not messages:
            return f"No emails found matching: {query}"
        output = [f"Found {len(messages)} emails matching '{query}':\n"]
        for msg_ref in messages[:10]:
            msg = service.users().messages().get(userId="me", id=msg_ref["id"], format="metadata", metadataHeaders=["From", "Subject", "Date"]).execute()
            headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
            output.append(f"- ID: {msg_ref['id']}")
            output.append(f"  From: {headers.get('From', 'Unknown')}")
            output.append(f"  Subject: {headers.get('Subject', 'No subject')}")
            output.append(f"  Date: {headers.get('Date', 'Unknown')}\n")
        return "\n".join(output)

    def _reply_email(self, service, message_id: str, body: str) -> str:
        original = service.users().messages().get(userId="me", id=message_id, format="metadata", metadataHeaders=["From", "Subject", "Message-ID"]).execute()
        headers = {h["name"]: h["value"] for h in original["payload"]["headers"]}
        reply = MIMEText(body)
        reply["to"] = headers.get("From", "")
        reply["subject"] = f"Re: {headers.get('Subject', '')}"
        reply["In-Reply-To"] = headers.get("Message-ID", "")
        reply["References"] = headers.get("Message-ID", "")
        raw = base64.urlsafe_b64encode(reply.as_bytes()).decode()
        result = service.users().messages().send(userId="me", body={"raw": raw, "threadId": original["threadId"]}).execute()
        return f"Reply sent successfully. Message ID: {result['id']}"
