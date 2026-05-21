"""
Reddit tool - search posts, get comments.
"""
import os
from tools.base import BaseTool
class RedditTool(BaseTool):
    name = "reddit"
    description = """Search Reddit posts and get top comments.
    Actions: 'search' (query, subreddit), 'hot' (subreddit, limit=10), 'comments' (url)"""
    category = "Web & Research"
    required_env_vars = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET"))
    def _get_reddit(self):
        import praw
        return praw.Reddit(client_id=os.getenv("REDDIT_CLIENT_ID"), client_secret=os.getenv("REDDIT_CLIENT_SECRET"), user_agent=os.getenv("REDDIT_USER_AGENT", "AgenticAI/1.0"))
    def _run(self, action: str, query: str = None, subreddit: str = None, url: str = None, limit: int = 10, **kwargs) -> str:
        reddit = self._get_reddit()
        if action == "search":
            if not query:
                return "Error: 'search' requires 'query'"
            sub = reddit.subreddit(subreddit) if subreddit else reddit.subreddit("all")
            posts = list(sub.search(query, limit=limit))
            return "Results:\n" + "\n".join(f"- [{p.score}] {p.title}" for p in posts)
        elif action == "hot":
            if not subreddit:
                return "Error: 'hot' requires 'subreddit'"
            posts = list(reddit.subreddit(subreddit).hot(limit=limit))
            return f"Hot in r/{subreddit}:\n" + "\n".join(f"- [{p.score}] {p.title}" for p in posts)
        return f"Error: Unknown action '{action}'"
