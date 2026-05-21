"""
Configuration management - loads all settings from environment variables.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Security
    # Set this to a strong random string to enable API key auth on all endpoints.
    # Leave blank to disable auth (fine for local development).
    API_SECRET_KEY: Optional[str] = os.getenv("API_SECRET_KEY") or None

    # CORS — comma-separated list of allowed origins.
    # Defaults to localhost only. Set to "*" only if you know what you're doing.
    ALLOWED_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
        if o.strip()
    ]

    # LLM API Keys
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Memory
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./data/chroma")

    # Communication tools
    GMAIL_CREDENTIALS_JSON: Optional[str] = os.getenv("GMAIL_CREDENTIALS_JSON")
    GMAIL_TOKEN_JSON: Optional[str] = os.getenv("GMAIL_TOKEN_JSON")
    SLACK_BOT_TOKEN: Optional[str] = os.getenv("SLACK_BOT_TOKEN")
    OUTLOOK_CLIENT_ID: Optional[str] = os.getenv("OUTLOOK_CLIENT_ID")
    OUTLOOK_CLIENT_SECRET: Optional[str] = os.getenv("OUTLOOK_CLIENT_SECRET")
    OUTLOOK_TENANT_ID: Optional[str] = os.getenv("OUTLOOK_TENANT_ID")
    DISCORD_BOT_TOKEN: Optional[str] = os.getenv("DISCORD_BOT_TOKEN")
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")
    ZOOM_CLIENT_ID: Optional[str] = os.getenv("ZOOM_CLIENT_ID")
    ZOOM_CLIENT_SECRET: Optional[str] = os.getenv("ZOOM_CLIENT_SECRET")
    ZOOM_ACCOUNT_ID: Optional[str] = os.getenv("ZOOM_ACCOUNT_ID")
    NOTION_API_KEY: Optional[str] = os.getenv("NOTION_API_KEY")

    # Productivity tools
    GOOGLE_CALENDAR_CREDENTIALS_JSON: Optional[str] = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_JSON")
    GOOGLE_CALENDAR_TOKEN_JSON: Optional[str] = os.getenv("GOOGLE_CALENDAR_TOKEN_JSON")
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    JIRA_URL: Optional[str] = os.getenv("JIRA_URL")
    JIRA_EMAIL: Optional[str] = os.getenv("JIRA_EMAIL")
    JIRA_API_TOKEN: Optional[str] = os.getenv("JIRA_API_TOKEN")
    LINEAR_API_KEY: Optional[str] = os.getenv("LINEAR_API_KEY")
    TODOIST_API_TOKEN: Optional[str] = os.getenv("TODOIST_API_TOKEN")
    ASANA_ACCESS_TOKEN: Optional[str] = os.getenv("ASANA_ACCESS_TOKEN")
    TRELLO_API_KEY: Optional[str] = os.getenv("TRELLO_API_KEY")
    TRELLO_API_TOKEN: Optional[str] = os.getenv("TRELLO_API_TOKEN")
    AIRTABLE_API_KEY: Optional[str] = os.getenv("AIRTABLE_API_KEY")
    GOOGLE_TASKS_CREDENTIALS_JSON: Optional[str] = os.getenv("GOOGLE_TASKS_CREDENTIALS_JSON")
    GOOGLE_TASKS_TOKEN_JSON: Optional[str] = os.getenv("GOOGLE_TASKS_TOKEN_JSON")

    # Files & Storage
    GOOGLE_DRIVE_CREDENTIALS_JSON: Optional[str] = os.getenv("GOOGLE_DRIVE_CREDENTIALS_JSON")
    GOOGLE_DRIVE_TOKEN_JSON: Optional[str] = os.getenv("GOOGLE_DRIVE_TOKEN_JSON")
    DROPBOX_ACCESS_TOKEN: Optional[str] = os.getenv("DROPBOX_ACCESS_TOKEN")
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    GOOGLE_DOCS_CREDENTIALS_JSON: Optional[str] = os.getenv("GOOGLE_DOCS_CREDENTIALS_JSON")
    GOOGLE_DOCS_TOKEN_JSON: Optional[str] = os.getenv("GOOGLE_DOCS_TOKEN_JSON")
    GOOGLE_SHEETS_CREDENTIALS_JSON: Optional[str] = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON")
    GOOGLE_SHEETS_TOKEN_JSON: Optional[str] = os.getenv("GOOGLE_SHEETS_TOKEN_JSON")

    # Web & Research
    TAVILY_API_KEY: Optional[str] = os.getenv("TAVILY_API_KEY")
    WOLFRAM_APP_ID: Optional[str] = os.getenv("WOLFRAM_APP_ID")
    NEWS_API_KEY: Optional[str] = os.getenv("NEWS_API_KEY")
    OPENWEATHERMAP_API_KEY: Optional[str] = os.getenv("OPENWEATHERMAP_API_KEY")
    REDDIT_CLIENT_ID: Optional[str] = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: Optional[str] = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "AgenticAI/1.0")

    # Finance
    STRIPE_API_KEY: Optional[str] = os.getenv("STRIPE_API_KEY")
    SHOPIFY_SHOP_URL: Optional[str] = os.getenv("SHOPIFY_SHOP_URL")
    SHOPIFY_ACCESS_TOKEN: Optional[str] = os.getenv("SHOPIFY_ACCESS_TOKEN")

    # AI & Dev
    E2B_API_KEY: Optional[str] = os.getenv("E2B_API_KEY")
    GOOGLE_VISION_CREDENTIALS_JSON: Optional[str] = os.getenv("GOOGLE_VISION_CREDENTIALS_JSON")
    HUGGINGFACE_API_TOKEN: Optional[str] = os.getenv("HUGGINGFACE_API_TOKEN")
    PINECONE_API_KEY: Optional[str] = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: Optional[str] = os.getenv("PINECONE_ENVIRONMENT")

    # Lifestyle
    SPOTIFY_CLIENT_ID: Optional[str] = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET: Optional[str] = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_REDIRECT_URI: Optional[str] = os.getenv("SPOTIFY_REDIRECT_URI")
    HUNTER_API_KEY: Optional[str] = os.getenv("HUNTER_API_KEY")

    def __init__(self):
        Path(self.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)


settings = Settings()
