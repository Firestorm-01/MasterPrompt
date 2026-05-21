"""
Spotify tool - search tracks, get recommendations.
"""
import os
from tools.base import BaseTool
class SpotifyTool(BaseTool):
    name = "spotify"
    description = """Search Spotify and get recommendations.
    Actions: 'search' (query, type='track'), 'recommendations' (seed_tracks=[])"""
    category = "Lifestyle"
    required_env_vars = ["SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("SPOTIFY_CLIENT_ID") and os.getenv("SPOTIFY_CLIENT_SECRET"))
    def _get_token(self) -> str:
        import httpx, base64
        credentials = base64.b64encode(f"{os.getenv('SPOTIFY_CLIENT_ID')}:{os.getenv('SPOTIFY_CLIENT_SECRET')}".encode()).decode()
        with httpx.Client() as client:
            return client.post("https://accounts.spotify.com/api/token", headers={"Authorization": f"Basic {credentials}"}, data={"grant_type": "client_credentials"}).json()["access_token"]
    def _run(self, action: str, query: str = None, type: str = "track", seed_tracks: list = None, **kwargs) -> str:
        import httpx
        headers = {"Authorization": f"Bearer {self._get_token()}"}
        if action == "search":
            if not query:
                return "Error: 'search' requires 'query'"
            with httpx.Client() as client:
                data = client.get("https://api.spotify.com/v1/search", headers=headers, params={"q": query, "type": type, "limit": 10}).json()
            items = data.get(f"{type}s", {}).get("items", [])
            if type == "track":
                return "Tracks:\n" + "\n".join(f"- {i['name']} by {', '.join(a['name'] for a in i['artists'])}" for i in items)
            return "Results:\n" + "\n".join(f"- {i['name']}" for i in items)
        return f"Error: Unknown action '{action}'"
