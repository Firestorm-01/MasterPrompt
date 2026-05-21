"""
PDF reader tool - extract, chunk, and summarize PDF content (FREE).
"""
import os
from typing import Optional
from tools.base import BaseTool
class PDFReaderTool(BaseTool):
    name = "pdf_reader"
    description = """Extract and analyze text from PDF files. FREE - no API key required.
    Actions: 'extract' (file_path), 'summary' (file_path), 'search' (file_path, query)"""
    category = "AI & Dev"
    required_env_vars = []
    is_free = True
    def is_available(self) -> bool:
        try:
            import pdfplumber
            return True
        except ImportError:
            return False
    def _run(self, file_path: str, action: str = "extract", query: str = None, max_pages: int = 50, **kwargs) -> str:
        import pdfplumber
        if file_path.startswith(("http://", "https://")):
            import httpx, tempfile
            resp = httpx.get(file_path, follow_redirects=True)
            fd, file_path = tempfile.mkstemp(suffix=".pdf")
            with os.fdopen(fd, "wb") as f:
                f.write(resp.content)
        if not os.path.exists(file_path):
            return f"Error: File not found: {file_path}"
        if action == "extract":
            output = []
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages[:max_pages]):
                    text = page.extract_text() or ""
                    if text.strip():
                        output.append(f"--- Page {i+1} ---\n{text[:2000]}")
            return "\n\n".join(output)[:10000]
        elif action == "search":
            if not query:
                return "Error: 'search' requires 'query'"
            results = []
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    if query.lower() in text.lower():
                        for line in text.split("\n"):
                            if query.lower() in line.lower():
                                results.append(f"Page {i+1}: {line.strip()[:200]}")
            if not results:
                return f"No matches for '{query}'"
            return f"Found {len(results)} matches:\n" + "\n".join(results[:20])
        return f"Error: Unknown action '{action}'"
