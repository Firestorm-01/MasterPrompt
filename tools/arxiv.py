"""
arXiv tool - search research papers (FREE).
"""
from tools.base import BaseTool
class ArxivTool(BaseTool):
    name = "arxiv"
    description = """Search arXiv for research papers. FREE - no API key required.
    Parameters: query (search terms), max_results (default 10)"""
    category = "Web & Research"
    required_env_vars = []
    is_free = True
    def is_available(self) -> bool:
        try:
            import arxiv
            return True
        except ImportError:
            return False
    def _run(self, query: str, max_results: int = 10, **kwargs) -> str:
        import arxiv
        search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
        results = list(search.results())
        if not results:
            return f"No papers found for '{query}'"
        output = [f"arXiv papers for '{query}':\n"]
        for paper in results:
            output.append(f"**{paper.title}**")
            output.append(f"Authors: {', '.join(a.name for a in paper.authors[:3])}")
            output.append(f"PDF: {paper.pdf_url}")
            output.append(f"Abstract: {paper.summary[:300]}...\n")
        return "\n".join(output)
