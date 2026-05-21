"""
Google Calendar tool - create, read, delete events, check availability.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Optional
from tools.base import BaseTool
class GoogleCalendarTool(BaseTool):
    name = "google_calendar"
    description = """Manage Google Calendar events.
    Actions: 'create' (summary, start, end, description='', attendees=[]),
    'list' (time_min, time_max, max_results=10), 'delete' (event_id), 'free_slots' (date, duration_minutes=60)
    Datetime format: ISO 8601 (e.g., '2024-01-15T10:00:00')"""
    category = "Productivity"
    required_env_vars = ["GOOGLE_CALENDAR_CREDENTIALS_JSON", "GOOGLE_CALENDAR_TOKEN_JSON"]
    is_free = False
    def __init__(self):
        self._service = None
    def is_available(self) -> bool:
        return bool(os.getenv("GOOGLE_CALENDAR_CREDENTIALS_JSON") and os.getenv("GOOGLE_CALENDAR_TOKEN_JSON"))
    def _get_service(self):
        if self._service:
            return self._service
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        token_data = json.loads(os.getenv("GOOGLE_CALENDAR_TOKEN_JSON"))
        creds = Credentials.from_authorized_user_info(token_data)
        self._service = build("calendar", "v3", credentials=creds)
        return self._service
    def _run(self, action: str, summary: Optional[str] = None, start: Optional[str] = None,
             end: Optional[str] = None, description: str = "", attendees: list = None,
             event_id: Optional[str] = None, time_min: Optional[str] = None,
             time_max: Optional[str] = None, max_results: int = 10, date: Optional[str] = None,
             duration_minutes: int = 60, **kwargs) -> str:
        service = self._get_service()
        if action == "create":
            if not all([summary, start, end]):
                return "Error: 'create' requires 'summary', 'start', and 'end'"
            event = {
                "summary": summary, "description": description,
                "start": {"dateTime": start, "timeZone": "UTC"},
                "end": {"dateTime": end, "timeZone": "UTC"},
            }
            if attendees:
                event["attendees"] = [{"email": e} for e in attendees]
            result = service.events().insert(calendarId="primary", body=event).execute()
            return f"Event created: '{summary}'. Event ID: {result['id']}"
        elif action == "list":
            now = datetime.utcnow()
            tmin = time_min or (now.isoformat() + "Z")
            tmax = time_max or ((now + timedelta(days=7)).isoformat() + "Z")
            events_result = service.events().list(
                calendarId="primary", timeMin=tmin, timeMax=tmax,
                maxResults=max_results, singleEvents=True, orderBy="startTime"
            ).execute()
            events = events_result.get("items", [])
            if not events:
                return "No upcoming events found."
            return "Events:\n" + "\n".join(f"- {e['summary']}: {e['start'].get('dateTime', e['start'].get('date'))}" for e in events)
        elif action == "delete":
            if not event_id:
                return "Error: 'delete' requires 'event_id'"
            service.events().delete(calendarId="primary", eventId=event_id).execute()
            return f"Event {event_id} deleted."
        return f"Error: Unknown action '{action}'"
