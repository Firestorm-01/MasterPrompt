"""
OCR tool - extract text from images.
"""
import os
from tools.base import BaseTool
class OCRTool(BaseTool):
    name = "ocr"
    description = """Extract text from images using OCR.
    Parameters: image_url or image_path"""
    category = "AI & Dev"
    required_env_vars = []
    is_free = True
    def is_available(self) -> bool:
        try:
            import pytesseract
            return True
        except ImportError:
            return False
    def _run(self, image_url: str = None, image_path: str = None, **kwargs) -> str:
        import pytesseract
        from PIL import Image
        import io
        if image_url:
            import httpx
            with httpx.Client() as client:
                resp = client.get(image_url)
            image = Image.open(io.BytesIO(resp.content))
        elif image_path:
            image = Image.open(image_path)
        else:
            return "Error: Provide 'image_url' or 'image_path'"
        text = pytesseract.image_to_string(image)
        return f"Extracted text:\n\n{text}" if text.strip() else "No text detected."
