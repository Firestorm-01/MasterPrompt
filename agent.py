"""
LangGraph ReAct agent implementation.
Implements the reason → act → observe → repeat loop for autonomous tool chaining.
"""
import asyncio
from typing import AsyncGenerator, Literal
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from config import settings
from memory import MemoryManager
from tools.registry import ToolRegistry


SYSTEM_PROMPT = """You are a highly capable AI assistant with access to various tools.
Your goal is to help users by autonomously chaining multiple tools to complete complex tasks.

## Available Tools
{tool_descriptions}

## Instructions
1. Analyze the user's request carefully
2. Break down complex tasks into steps
3. Use tools autonomously - don't ask for permission, just execute
4. Chain multiple tools when needed to complete the task
5. If a tool fails, try an alternative approach or report what happened
6. Always provide a clear final answer summarizing what you accomplished

## Context from Previous Conversations
{context}

## Guidelines
- Be proactive and take action without asking for confirmation
- When creating content (documents, tickets, messages), include all relevant details
- If you need information you don't have, use appropriate tools to find it
- Report both successes and failures clearly"""


class AgentRunner:
    """Manages the LangGraph ReAct agent execution."""

    def __init__(self, tool_registry: ToolRegistry, memory: MemoryManager):
        self.tool_registry = tool_registry
        self.memory = memory
        self.llm = self._initialize_llm()
        self.graph = self._build_graph()

    def _initialize_llm(self):
        """Initialize primary LLM with fallback."""
        if settings.GROQ_API_KEY:
            return ChatGroq(
                api_key=settings.GROQ_API_KEY,
                model_name="llama-3.3-70b-versatile",
                temperature=0.1,
                max_tokens=4096
            )
        elif settings.ANTHROPIC_API_KEY:
            return ChatAnthropic(
                api_key=settings.ANTHROPIC_API_KEY,
                model="claude-sonnet-4-20250514",
                temperature=0.1,
                max_tokens=4096
            )
        else:
            raise ValueError("No LLM API key configured. Set GROQ_API_KEY or ANTHROPIC_API_KEY.")

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine."""
        tools = self.tool_registry.get_langchain_tools()

        llm_with_tools = self.llm.bind_tools(tools) if tools else self.llm

        def should_continue(state: dict) -> Literal["tools", "end"]:
            messages = state.get("messages", [])
            if not messages:
                return "end"
            last = messages[-1]
            if state.get("current_step", 0) >= state.get("max_steps", 15):
                return "end"
            if hasattr(last, "tool_calls") and last.tool_calls:
                return "tools"
            return "end"

        def agent_node(state: dict) -> dict:
            messages = state.get("messages", [])
            response = llm_with_tools.invoke(messages)
            return {
                **state,
                "messages": messages + [response],
                "current_step": state.get("current_step", 0) + 1
            }

        def tool_node(state: dict) -> dict:
            messages = state.get("messages", [])
            last = messages[-1]
            tool_results = []

            if hasattr(last, "tool_calls"):
                for tool_call in last.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    tool = self.tool_registry.get_tool_by_name(tool_name)
                    if tool:
                        try:
                            result = tool.safe_run(tool_args)
                        except Exception as e:
                            result = f"Error executing {tool_name}: {str(e)}"
                    else:
                        result = f"Tool '{tool_name}' not found or not available"

                    tool_results.append(
                        ToolMessage(content=str(result), tool_call_id=tool_call["id"])
                    )

            return {
                **state,
                "messages": messages + tool_results,
                "tool_results": state.get("tool_results", []) + tool_results
            }

        workflow = StateGraph(dict)
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
        workflow.add_edge("tools", "agent")
        return workflow.compile()

    async def run_stream(
        self,
        message: str,
        session_id: str,
        context: str = "",
        history: list[dict] = None
    ) -> AsyncGenerator[dict, None]:
        """Execute the agent and stream events."""
        history = history or []
        tool_descriptions = self._format_tool_descriptions()

        messages = [
            SystemMessage(content=SYSTEM_PROMPT.format(
                tool_descriptions=tool_descriptions,
                context=context or "No previous context available."
            ))
        ]

        for msg in history[-20:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=message))

        initial_state = {
            "messages": messages,
            "current_step": 0,
            "max_steps": 15,
            "tool_results": [],
        }

        final_state = initial_state

        try:
            previous_count = len(messages)

            async for state in self._stream_graph(initial_state):
                final_state = state
                current_messages = state.get("messages", [])

                for msg in current_messages[previous_count:]:
                    if isinstance(msg, AIMessage):
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            for tc in msg.tool_calls:
                                yield {"type": "tool_call", "tool": tc["name"], "args": tc["args"]}
                        if msg.content:
                            yield {"type": "thought", "content": msg.content}

                    elif isinstance(msg, ToolMessage):
                        yield {"type": "tool_result", "content": msg.content[:500]}

                previous_count = len(current_messages)

            # Yield final answer from last AI message
            for msg in reversed(final_state.get("messages", [])):
                if isinstance(msg, AIMessage) and msg.content:
                    yield {"type": "final_answer", "content": msg.content}
                    self.memory.add_message(session_id, "user", message)
                    self.memory.add_message(session_id, "assistant", msg.content)
                    self.memory.extract_and_store_facts(session_id, message, msg.content)
                    break

        except Exception as e:
            yield {"type": "error", "content": f"Agent error: {str(e)}"}

    async def _stream_graph(self, initial_state: dict) -> AsyncGenerator[dict, None]:
        """Run graph in executor to avoid blocking the event loop."""
        loop = asyncio.get_event_loop()

        def run_sync():
            states = []
            for chunk in self.graph.stream(initial_state):
                for node_state in chunk.values():
                    states.append(node_state)
            return states

        states = await loop.run_in_executor(None, run_sync)
        for state in states:
            yield state

    def _format_tool_descriptions(self) -> str:
        tools = self.tool_registry.available_tools
        if not tools:
            return "No tools currently available."
        return "\n".join(f"- **{t.name}**: {t.description}" for t in tools)
