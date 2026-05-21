"""
Memory management using ChromaDB for short-term and long-term storage.
Handles conversation history and fact extraction for context retrieval.
"""
import hashlib
import json
from datetime import datetime
from typing import Optional
import chromadb
from config import settings


class MemoryManager:
    """Manages short-term conversation history and long-term fact storage."""

    def __init__(self):
        # Use modern ChromaDB PersistentClient API (v0.4+)
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR
        )

        self.conversations = self.client.get_or_create_collection(
            name="conversations",
            metadata={"description": "Conversation history by session"}
        )

        self.facts = self.client.get_or_create_collection(
            name="facts",
            metadata={"description": "Extracted facts from conversations"}
        )

        self._message_cache: dict[str, list[dict]] = {}

    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to conversation history."""
        timestamp = datetime.utcnow().isoformat()
        message_id = hashlib.sha256(
            f"{session_id}{timestamp}{content}".encode()
        ).hexdigest()[:16]

        message = {"role": role, "content": content, "timestamp": timestamp}

        self.conversations.add(
            documents=[content],
            metadatas=[{"session_id": session_id, "role": role, "timestamp": timestamp}],
            ids=[message_id]
        )

        if session_id not in self._message_cache:
            self._message_cache[session_id] = []
        self._message_cache[session_id].append(message)

        if len(self._message_cache[session_id]) > 50:
            self._message_cache[session_id] = self._message_cache[session_id][-50:]

    def get_conversation_history(self, session_id: str, limit: int = 20) -> list[dict]:
        """Get recent conversation history for a session."""
        if session_id in self._message_cache:
            return self._message_cache[session_id][-limit:]

        results = self.conversations.get(
            where={"session_id": session_id},
            include=["documents", "metadatas"]
        )

        messages = []
        if results and results["documents"]:
            for doc, meta in zip(results["documents"], results["metadatas"]):
                messages.append({
                    "role": meta["role"],
                    "content": doc,
                    "timestamp": meta.get("timestamp", "")
                })

        messages.sort(key=lambda x: x.get("timestamp", ""))
        messages = messages[-limit:]
        self._message_cache[session_id] = messages
        return messages

    def extract_and_store_facts(self, session_id: str, user_message: str, assistant_response: str):
        """Extract and store important facts from the conversation."""
        facts_to_store = self._extract_facts(user_message, assistant_response)

        for fact in facts_to_store:
            fact_id = hashlib.sha256(f"{session_id}{fact}".encode()).hexdigest()[:16]
            try:
                self.facts.add(
                    documents=[fact],
                    metadatas=[{
                        "session_id": session_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "source": "conversation"
                    }],
                    ids=[fact_id]
                )
            except Exception:
                pass

    def _extract_facts(self, user_message: str, assistant_response: str) -> list[str]:
        indicators = [
            "my name is", "i am", "i work", "i live", "my email",
            "i prefer", "i like", "i need", "i want", "i use",
            "my company", "my team", "my project", "my goal"
        ]
        facts = []
        combined = f"{user_message} {assistant_response}".lower()
        for indicator in indicators:
            if indicator in combined:
                for sentence in combined.split("."):
                    if indicator in sentence:
                        clean = sentence.strip()
                        if 10 < len(clean) < 200:
                            facts.append(clean)
        return facts[:5]

    def retrieve_context(self, query: str, session_id: str, n_results: int = 5) -> str:
        """Retrieve relevant context from long-term memory."""
        try:
            # Only query if there are facts stored for this session
            existing = self.facts.get(where={"session_id": session_id})
            if not existing or not existing["ids"]:
                return ""

            count = len(existing["ids"])
            results = self.facts.query(
                query_texts=[query],
                n_results=min(n_results, count),
                where={"session_id": session_id}
            )

            if results and results["documents"] and results["documents"][0]:
                facts = results["documents"][0]
                return "Remembered facts:\n" + "\n".join(f"- {fact}" for fact in facts)
        except Exception:
            pass
        return ""

    def clear_session(self, session_id: str):
        """Clear all data for a session."""
        if session_id in self._message_cache:
            del self._message_cache[session_id]

        try:
            conv_results = self.conversations.get(where={"session_id": session_id})
            if conv_results and conv_results["ids"]:
                self.conversations.delete(ids=conv_results["ids"])

            fact_results = self.facts.get(where={"session_id": session_id})
            if fact_results and fact_results["ids"]:
                self.facts.delete(ids=fact_results["ids"])
        except Exception:
            pass

    def close(self):
        """ChromaDB PersistentClient auto-persists; nothing to do."""
        pass
