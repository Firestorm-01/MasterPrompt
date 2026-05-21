"""
FastAPI application with SSE streaming endpoint for the agentic AI assistant.
Handles chat requests, streams agent reasoning steps, and manages tool execution.
"""
import asyncio
import json
import os
import secrets
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agent import AgentRunner
from config import settings
from memory import MemoryManager
from tools.registry import ToolRegistry


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.tool_registry = ToolRegistry()
    app.state.memory = MemoryManager()
    app.state.agent = AgentRunner(
        tool_registry=app.state.tool_registry,
        memory=app.state.memory
    )
    yield
    app.state.memory.close()


app = FastAPI(
    title="Agentic AI Assistant",
    description="Production-ready AI agent with 50+ tool integrations",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Optional API key auth — enabled when API_SECRET_KEY is set in .env
# ---------------------------------------------------------------------------

def verify_api_key(x_api_key: str | None = Header(default=None)):
    """Validate X-API-Key header if API_SECRET_KEY is configured."""
    required = settings.API_SECRET_KEY
    if required:
        if not x_api_key or not secrets.compare_digest(x_api_key, required):
            raise HTTPException(status_code=401, detail="Invalid or missing API key")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ConfigUpdateRequest(BaseModel):
    env_vars: dict[str, str]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/tools", dependencies=[Depends(verify_api_key)])
async def list_tools(request: Request):
    registry: ToolRegistry = request.app.state.tool_registry
    tools_info = [
        {
            "name": tool.name,
            "description": tool.description,
            "category": tool.category,
            "is_available": tool.is_available(),
            "required_env_vars": tool.required_env_vars,
            "is_free": tool.is_free,
        }
        for tool in registry.all_tools
    ]
    return {
        "tools": tools_info,
        "available_count": len(registry.available_tools),
        "total_count": len(registry.all_tools),
    }


@app.post("/config", dependencies=[Depends(verify_api_key)])
async def update_config(request: Request, config: ConfigUpdateRequest):
    for key, value in config.env_vars.items():
        if value:
            os.environ[key] = value

    request.app.state.tool_registry = ToolRegistry()
    request.app.state.agent = AgentRunner(
        tool_registry=request.app.state.tool_registry,
        memory=request.app.state.memory
    )
    return {
        "status": "updated",
        "available_tools": len(request.app.state.tool_registry.available_tools)
    }


@app.post("/chat", dependencies=[Depends(verify_api_key)])
async def chat(request: Request, chat_request: ChatRequest):
    """Stream chat responses via Server-Sent Events."""
    agent: AgentRunner = request.app.state.agent
    memory: MemoryManager = request.app.state.memory

    async def event_stream() -> AsyncGenerator[str, None]:
        try:
            context = memory.retrieve_context(chat_request.message, chat_request.session_id)
            history = memory.get_conversation_history(chat_request.session_id)

            async for event in agent.run_stream(
                message=chat_request.message,
                session_id=chat_request.session_id,
                context=context,
                history=history
            ):
                yield f"data: {json.dumps(event)}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/history/{session_id}", dependencies=[Depends(verify_api_key)])
async def get_history(request: Request, session_id: str):
    memory: MemoryManager = request.app.state.memory
    history = memory.get_conversation_history(session_id)
    return {"session_id": session_id, "messages": history}


@app.delete("/history/{session_id}", dependencies=[Depends(verify_api_key)])
async def clear_history(request: Request, session_id: str):
    memory: MemoryManager = request.app.state.memory
    memory.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
