"""Tavily Search tool — AI-native web search for agents."""

from typing import Any, Dict, List, Optional

from tavily import TavilyClient

from app.config.logging_config import get_logger
from app.config.settings import settings


class TavilySearchTool:
    """
    Wrapper around the Tavily search API.

    Tavily returns LLM-ready, structured results (title, url, content)
    specifically optimized for autonomous agents.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.logger = get_logger(__name__)
        self.api_key = api_key or settings.TAVILY_API_KEY
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY is not configured.")
        self.client = TavilyClient(api_key=self.api_key)

    def search(
        self,
        query: str,
        max_results: int = None,
        search_depth: str = None,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform a web search and return normalized results.

        Returns a list of dicts with keys:
        - title: str
        - url: str
        - content: str
        - score: float
        - published_date: Optional[str]
        """
        max_results = max_results or settings.TAVILY_MAX_RESULTS
        search_depth = search_depth or settings.TAVILY_SEARCH_DEPTH

        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                include_answer=False,
                include_raw_content=False,
            )
        except Exception as exc:
            self.logger.error(f"Tavily search failed for '{query}': {exc}")
            return []

        results: List[Dict[str, Any]] = []
        for r in response.get("results", []):
            results.append(
                {
                    "title": r.get("title"),
                    "url": r.get("url"),
                    "content": r.get("content") or r.get("raw_content") or "",
                    "score": r.get("score", 0.0),
                    "published_date": r.get("published_date"),
                }
            )
        self.logger.info(f"Tavily returned {len(results)} results for '{query[:60]}'")
        return results

    def search_news(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Convenience method that biases toward recent news."""
        return self.search(
            query=f"{query} latest news",
            max_results=max_results,
            search_depth="advanced",
        )