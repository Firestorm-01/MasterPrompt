"""
Hugging Face tool - run inference on models.
"""
import os
from tools.base import BaseTool
class HuggingFaceTool(BaseTool):
    name = "huggingface"
    description = """Run inference on Hugging Face models.
    Parameters: model (model ID), inputs (text input), task (optional)"""
    category = "AI & Dev"
    required_env_vars = ["HUGGINGFACE_API_TOKEN"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("HUGGINGFACE_API_TOKEN"))
    def _run(self, model: str, inputs: str, task: str = None, **kwargs) -> str:
        from huggingface_hub import InferenceClient
        client = InferenceClient(token=os.getenv("HUGGINGFACE_API_TOKEN"))
        result = client.text_generation(inputs, model=model, max_new_tokens=256)
        return f"Output:\n{result}"
