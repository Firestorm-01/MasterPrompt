"""
Image generation tool - DALL-E 3 via OpenAI.
"""
import os
from tools.base import BaseTool
class ImageGenerationTool(BaseTool):
    name = "image_generation"
    description = """Generate images using DALL-E 3.
    Parameters: prompt (description of image), size ('1024x1024', '1792x1024', '1024x1792')"""
    category = "AI & Dev"
    required_env_vars = ["OPENAI_API_KEY"]
    is_free = False
    def is_available(self) -> bool:
        return bool(os.getenv("OPENAI_API_KEY"))
    def _run(self, prompt: str, size: str = "1024x1024", **kwargs) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.images.generate(model="dall-e-3", prompt=prompt, size=size, quality="standard", n=1)
        return f"Image generated!\nURL: {response.data[0].url}"
