"""
Wolfram Alpha tool - computational queries.
"""
import os
from tools.base import BaseTool
class WolframAlphaTool(BaseTool):
    name = "wolfram_alpha"
    description = """Query Wolfram Alpha for computations, math, science, and factual data.
    Parameters: query (the question or computation)"""
    category = "Web & Research"
    required_env_vars = ["WOLFRAM_APP_ID"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("WOLFRAM_APP_ID"))
    def _run(self, query: str, **kwargs) -> str:
        import wolframalpha
        client = wolframalpha.Client(os.getenv("WOLFRAM_APP_ID"))
        res = client.query(query)
        output = [f"Wolfram Alpha: {query}\n"]
        for pod in res.pods:
            output.append(f"**{pod.title}**")
            for sub in pod.subpods:
                if sub.plaintext:
                    output.append(sub.plaintext)
        return "\n".join(output) if len(output) > 1 else "No results found."
