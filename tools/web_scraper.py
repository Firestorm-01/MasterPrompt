"""
Web scraper tool - extracts clean text from any URL using Playwright.
"""
import os
from typing import Optional
from tools.base import BaseTool
class WebScraperTool(BaseTool):
    name = "web_scraper"
    description = """Scrape and extract clean text content from any webpage URL.
    Parameters: url (required), selector (optional CSS selector to target specific content)"""
    category = "Web & Research"
    required_env_vars = []
    is_free = True
    def is_available(self) -> bool:
        try:
            import playwright
            return True
        except ImportError:
            return False
    def _run(self, url: str, selector: Optional[str] = None, **kwargs) -> str:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            try:
                page.goto(url, timeout=30000)
                page.wait_for_load_state("domcontentloaded")
                title = page.title()
                if selector:
                    elements = page.query_selector_all(selector)
                    text_content = "\n\n".join(el.inner_text() for el in elements if el.inner_text().strip())
                else:
                    page.evaluate("document.querySelectorAll('script, style, nav, footer').forEach(el => el.remove());")
                    body = page.query_selector("body")
                    text_content = body.inner_text() if body else ""
                lines = [line.strip() for line in text_content.split("\n") if line.strip()]
                clean_text = "\n".join(lines)[:5000]
                return f"Page: {title}\nURL: {url}\n\n{clean_text}"
            finally:
                browser.close()
