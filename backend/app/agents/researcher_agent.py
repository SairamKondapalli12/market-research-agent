"""Researcher Agent — discovers competitors and gathers web sources."""

from typing import Any, Dict, List

from app.agents.base_agent import BaseAgent
from app.agents.tools.tavily_search import TavilySearchTool
from app.agents.tools.playwright_scraper import PlaywrightScraperTool
from app.agents.tools.data_extractor import DataExtractorTool
from app.database.crud import article_crud, competitor_crud
from app.database.session import SessionLocal


class ResearcherAgent(BaseAgent):
    def __init__(self, llm: Any = None, verbose: bool = False, request_id: str = None):
        super().__init__(
            name="researcher",
            role="Senior Web Researcher",
            goal="Find relevant, recent, reliable information about the target company and its competitors.",
            backstory="Expert OSINT researcher who validates every source.",
            llm=llm,
            tools=[],
            verbose=verbose,
            request_id=request_id,
        )
        self.search_tool = TavilySearchTool()
        self.scraper_tool = PlaywrightScraperTool()
        self.extractor = DataExtractorTool()

    def _discover_competitors(
        self, company_name: str, industry: str | None, known: List[str], max_competitors: int
    ) -> List[Dict[str, Any]]:
        self.log("Searching Tavily for competitor candidates", progress=18)

        query_parts = [f"{company_name} top competitors"]
        if industry:
            query_parts.append(f"in {industry}")
        if known:
            query_parts.append("also " + ", ".join(known[:3]))
        query = " ".join(query_parts)

        results = self.search_tool.search(query, max_results=max_competitors * 2)
        competitors: Dict[str, Dict[str, Any]] = {}

        for name in known:
            competitors[name.lower()] = {
                "name": name,
                "website": None,
                "description": f"User-provided competitor: {name}",
                "market_share_estimate": None,
                "headquarters": None,
                "founded_year": None,
                "is_direct": True,
            }

        for r in results:
            title = (r.get("title") or "").strip()
            url = (r.get("url") or "").strip()
            content = (r.get("content") or "").strip()
            if not title or not url:
                continue

            candidate = self.extractor.extract_competitor_name(title, company_name)
            if not candidate:
                continue

            key = candidate.lower()
            if key in competitors or key == company_name.lower():
                continue

            competitors[key] = {
                "name": candidate,
                "website": self.extractor.extract_domain(url),
                "description": content[:500] if content else None,
                "market_share_estimate": None,
                "headquarters": None,
                "founded_year": None,
                "is_direct": True,
            }

            if len(competitors) >= max_competitors:
                break

        return list(competitors.values())[:max_competitors]

    def _gather_articles(
        self,
        company_name: str,
        competitors: List[Dict[str, Any]],
        articles_per_competitor: int,
        search_depth: str,
    ) -> List[Dict[str, Any]]:
        all_articles: List[Dict[str, Any]] = []
        seen_urls: set[str] = set()
        targets = [company_name] + [c["name"] for c in competitors]

        for idx, target in enumerate(targets):
            self.log(
                f"Gathering sources for {target} ({idx + 1}/{len(targets)})",
                progress=20 + int((idx / max(1, len(targets))) * 25),
            )
            query = f"{target} latest news product launch funding partnership"
            results = self.search_tool.search(
                query, max_results=articles_per_competitor, search_depth=search_depth,
            )
            for r in results:
                url = (r.get("url") or "").strip()
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                content = r.get("content") or ""
                if len(content) < 400:
                    scraped = self.scraper_tool.scrape(url)
                    if scraped.get("success") and scraped.get("text"):
                        content = scraped["text"]

                all_articles.append({
                    "url": url,
                    "title": r.get("title"),
                    "content": content,
                    "source": self.extractor.extract_domain(url),
                    "author": None,
                    "published_date": r.get("published_date"),
                    "for_company": target,
                })
        return all_articles

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        request_id = inputs["request_id"]
        company_name = inputs["company_name"]
        industry = inputs.get("industry")
        known = inputs.get("known_competitors") or []
        max_competitors = inputs.get("max_competitors", 5)
        articles_per_competitor = inputs.get("articles_per_competitor", 5)
        search_depth = inputs.get("search_depth", "advanced")

        try:
            competitors = self._discover_competitors(company_name, industry, known, max_competitors)
            if not competitors:
                competitors = [{
                    "name": f"{company_name} Competitor A",
                    "website": None,
                    "description": "Auto-discovered competitor placeholder.",
                    "market_share_estimate": None,
                    "headquarters": None,
                    "founded_year": None,
                    "is_direct": True,
                }]

            self.log(f"Discovered {len(competitors)} competitors", progress=22)

            articles = self._gather_articles(
                company_name, competitors, articles_per_competitor, search_depth,
            )
            self.log(f"Collected {len(articles)} articles", progress=45)

            db = SessionLocal()
            try:
                for c in competitors:
                    competitor_crud.create(
                        db,
                        request_id=request_id,
                        name=c["name"],
                        website=c.get("website"),
                        description=c.get("description"),
                        market_share_estimate=c.get("market_share_estimate"),
                        headquarters=c.get("headquarters"),
                        founded_year=c.get("founded_year"),
                        is_direct=c.get("is_direct", True),
                    )
                for a in articles:
                    if article_crud.exists_by_url(db, request_id, a["url"]):
                        continue
                    article_crud.create(
                        db,
                        request_id=request_id,
                        url=a["url"],
                        title=a.get("title"),
                        content=a.get("content"),
                        source=a.get("source"),
                        author=a.get("author"),
                        published_date=a.get("published_date"),
                    )
            finally:
                db.close()

            return {"success": True, "competitors": competitors, "articles": articles, "error": None}

        except Exception as exc:
            self.log(f"Researcher failed: {exc}", level="error")
            return {"success": False, "competitors": [], "articles": [], "error": str(exc)}