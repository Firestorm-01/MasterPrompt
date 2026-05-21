"""
Hunter.io tool - find email addresses by domain.
"""
import os
import httpx
from tools.base import BaseTool
class HunterTool(BaseTool):
    name = "hunter"
    description = """Find email addresses for a company domain using Hunter.io.
    Actions: 'domain_search' (domain), 'email_finder' (domain, first_name, last_name)"""
    category = "Lifestyle"
    required_env_vars = ["HUNTER_API_KEY"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("HUNTER_API_KEY"))
    def _run(self, action: str, domain: str = None, first_name: str = None, last_name: str = None, **kwargs) -> str:
        api_key = os.getenv("HUNTER_API_KEY")
        if action == "domain_search":
            if not domain:
                return "Error: 'domain_search' requires 'domain'"
            with httpx.Client() as client:
                data = client.get("https://api.hunter.io/v2/domain-search", params={"domain": domain, "api_key": api_key}).json()
            emails = data.get("data", {}).get("emails", [])
            return f"Emails for {domain}:\n" + "\n".join(f"- {e['value']} ({e.get('type', 'unknown')})" for e in emails[:20])
        elif action == "email_finder":
            if not all([domain, first_name, last_name]):
                return "Error: 'email_finder' requires 'domain', 'first_name', 'last_name'"
            with httpx.Client() as client:
                data = client.get("https://api.hunter.io/v2/email-finder", params={"domain": domain, "first_name": first_name, "last_name": last_name, "api_key": api_key}).json()
            email = data.get("data", {}).get("email")
            return f"Found: {email}" if email else f"No email found for {first_name} {last_name} at {domain}"
        return f"Error: Unknown action '{action}'"
