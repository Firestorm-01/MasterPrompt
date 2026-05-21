"""
Pinecone tool - vector upsert and similarity search.
"""
import os
from tools.base import BaseTool
class PineconeTool(BaseTool):
    name = "pinecone"
    description = """Vector database operations with Pinecone.
    Actions: 'upsert' (index_name, vectors), 'query' (index_name, vector, top_k=5)"""
    category = "AI & Dev"
    required_env_vars = ["PINECONE_API_KEY", "PINECONE_ENVIRONMENT"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("PINECONE_API_KEY") and os.getenv("PINECONE_ENVIRONMENT"))
    def _run(self, action: str, index_name: str = None, vectors: list = None, vector: list = None, top_k: int = 5, **kwargs) -> str:
        from pinecone import Pinecone
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        if action == "upsert":
            if not all([index_name, vectors]):
                return "Error: 'upsert' requires 'index_name' and 'vectors'"
            pc.Index(index_name).upsert(vectors=vectors)
            return f"Upserted {len(vectors)} vectors to {index_name}"
        elif action == "query":
            if not all([index_name, vector]):
                return "Error: 'query' requires 'index_name' and 'vector'"
            results = pc.Index(index_name).query(vector=vector, top_k=top_k, include_metadata=True)
            return "Results:\n" + "\n".join(f"- {m.id}: {m.score:.4f}" for m in results.matches)
        return f"Error: Unknown action '{action}'"
