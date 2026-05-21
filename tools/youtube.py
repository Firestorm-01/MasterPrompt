"""
YouTube tool - search videos, fetch transcripts.
"""
from tools.base import BaseTool
class YouTubeTool(BaseTool):
    name = "youtube"
    description = """Search YouTube videos and get transcripts.
    Actions: 'search' (query, max_results=5), 'transcript' (video_id)"""
    category = "Web & Research"
    required_env_vars = []
    is_free = True
    def is_available(self) -> bool:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            return True
        except ImportError:
            return False
    def _run(self, action: str, query: str = None, video_id: str = None, max_results: int = 5, **kwargs) -> str:
        if action == "search":
            if not query:
                return "Error: 'search' requires 'query'"
            import httpx, re
            with httpx.Client() as client:
                resp = client.get("https://www.youtube.com/results", params={"search_query": query}, headers={"Accept-Language": "en-US,en"})
                video_ids = list(dict.fromkeys(re.findall(r'watch\?v=([a-zA-Z0-9_-]{11})', resp.text)))[:max_results]
            return f"YouTube results for '{query}':\n" + "\n".join(f"- https://youtube.com/watch?v={v}" for v in video_ids)
        elif action == "transcript":
            if not video_id:
                return "Error: 'transcript' requires 'video_id'"
            from youtube_transcript_api import YouTubeTranscriptApi
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                text = " ".join(e["text"] for e in transcript)
                return f"Transcript:\n\n{text[:5000]}"
            except Exception as e:
                return f"Could not get transcript: {str(e)}"
        return f"Error: Unknown action '{action}'"
