# Agentic AI Assistant

A production-ready AI agent with 50+ tool integrations, built with LangGraph ReAct loop, FastAPI SSE streaming, and a React frontend.

## Quick Start

### Backend
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env — add at least GROQ_API_KEY or ANTHROPIC_API_KEY
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

## Security

**API Key Auth** — set `API_SECRET_KEY` in `.env` to a strong random string:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
All endpoints then require `X-API-Key: <your key>` header. Leave blank for local dev.

**CORS** — set `ALLOWED_ORIGINS` to your frontend's URL. Defaults to localhost only.

## Structure
```
├── main.py            # FastAPI app + SSE streaming + auth
├── agent.py           # LangGraph ReAct agent
├── memory.py          # ChromaDB memory (PersistentClient)
├── config.py          # All settings from env vars
├── tools/
│   ├── base.py        # Abstract base + StructuredTool schema generation
│   ├── registry.py    # Auto-discovery
│   └── *.py           # 50+ individual tools
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── screens/   # Splash, Setup, Chat
│   ├── index.html
│   └── package.json
├── requirements.txt
└── .env.example
```

## Tool Categories
| Category | Tools |
|---|---|
| Communication | Gmail, Slack, Discord, Telegram, WhatsApp, Twilio SMS, Zoom, Outlook, Notion |
| Productivity | GitHub, Jira, Linear, Todoist, Asana, Trello, Airtable, Google Calendar, Google Tasks, Outlook Calendar |
| Files & Storage | Google Drive, Google Docs, Google Sheets, Dropbox, AWS S3, OneDrive, GitHub Gist |
| Web & Research | Web Search, Web Scraper, Wikipedia★, Wolfram Alpha, News API, Weather, YouTube★, Reddit, Hacker News★, arXiv★ |
| Finance | Stock Prices★, Crypto Prices★, Currency FX★, Stripe, Shopify |
| AI & Dev | Code Interpreter (E2B), Image Generation (DALL-E 3), OCR★, HuggingFace, Pinecone, PDF Reader★, Webhook★ |
| Lifestyle | Spotify, Hunter.io |

★ = free, no API key required

## Adding a New Tool
1. Create `tools/your_tool.py`
2. Extend `BaseTool`, set class vars, implement `_run()` and `is_available()`
3. Restart — it's auto-discovered

## What Was Fixed (vs original)
- **ChromaDB**: migrated from deprecated `duckdb+parquet` client to `PersistentClient`
- **Tool schemas**: `BaseTool.to_langchain_tool()` now uses `StructuredTool` with auto-generated Pydantic input models from each tool's `_run()` signature, so the LLM gets proper structured tool calling
- **Agent state**: node functions now preserve full state with `{**state, ...}` instead of returning partial dicts
- **Auth**: all endpoints protected by optional `X-API-Key` header (enabled via `API_SECRET_KEY` env var)
- **CORS**: replaced `allow_origins=["*"]` with configurable `ALLOWED_ORIGINS` defaulting to localhost only
- **Gmail**: restored the `read` and `reply` actions that were missing from the condensed version
- **Memory**: fixed `retrieve_context` to check collection size before querying to avoid ChromaDB errors on empty collections
# MasterPrompt
