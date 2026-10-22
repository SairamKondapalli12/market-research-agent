"""Confidence scoring for reports.

Confidence is a 0–100 integer derived from weighted signals that reflect
how much real, verifiable data the pipeline was able to gather.

It is NOT a percentage of correctness — it is a heuristic measure of
how well-supported the report's conclusions are by sources.
"""

from typing import Any, Dict, List

from app.config.logging_config import get_logger

logger = get_logger(__name__)


# High-credibility domains get a bonus; low-quality domains get a penalty
HIGH_CRED_DOMAINS = {
    "reuters.com", "bloomberg.com", "wsj.com", "ft.com",
    "techcrunch.com", "theverge.com", "wired.com", "arstechnica.com",
    "forbes.com", "businessinsider.com", "cnbc.com", "nytimes.com",
    "economist.com", "venturebeat.com", "protocol.com",
    "sec.gov", "gov.uk", "europa.eu",
}

LOW_CRED_DOMAINS = {
    "medium.com", "substack.com", "reddit.com", "quora.com",
    "youtube.com", "facebook.com", "twitter.com", "x.com",
    "linkedin.com", "wikipedia.org",
}


class ConfidenceService:

    @staticmethod
    def compute(
        *,
        articles: List[Dict[str, Any]],
        events: List[Any],
        competitors: List[Dict[str, Any]],
        sentiment: Dict[str, Any] | None = None,
        financials: Dict[str, Any] | None = None,
        llm_success_rate: float = 1.0,
    ) -> int:
        """
        Compute a real confidence score between 0 and 100.

        Each component contributes a weighted amount. The final result is
        clamped to [10, 98] so we never claim absolute certainty.
        """
        components: Dict[str, float] = {}

        # ─── 1. Source count (max 20 pts) ───────────────────
        article_count = len(articles)
        components["sources"] = min(20, article_count * 1.0)

        # ─── 2. Source credibility (max 15 pts) ─────────────
        if article_count > 0:
            high = 0
            low = 0
            neutral = 0
            for a in articles:
                domain = (a.get("source") or "").lower().strip()
                if domain in HIGH_CRED_DOMAINS:
                    high += 1
                elif domain in LOW_CRED_DOMAINS:
                    low += 1
                else:
                    neutral += 1
            score = (
                (high / article_count) * 15
                + (neutral / article_count) * 8
                + (low / article_count) * 2
            )
            components["credibility"] = round(score, 2)
        else:
            components["credibility"] = 0

        # ─── 3. Event density (max 20 pts) ──────────────────
        event_count = len(events)
        # Ideal: 1+ event per 3 articles, cap at 20
        if article_count > 0:
            density = event_count / max(1, article_count)
            components["events"] = min(20, density * 20)
        else:
            components["events"] = 0

        # ─── 4. Competitor discovery (max 15 pts) ───────────
        comp_count = len(competitors)
        # Ideal: 5+ competitors
        components["competitors"] = min(15, comp_count * 3.0)

        # ─── 5. Sentiment available (max 10 pts) ────────────
        if sentiment and len(sentiment) > 0:
            scored = sum(1 for v in sentiment.values() if v.get("overall_label"))
            components["sentiment"] = min(10, scored * 1.5)
        else:
            components["sentiment"] = 0

        # ─── 6. Financial data available (max 10 pts) ───────
        if financials and len(financials) > 0:
            with_data = sum(
                1 for v in financials.values()
                if v.get("total_raised") or v.get("latest_valuation")
            )
            components["financials"] = min(10, with_data * 2.0)
        else:
            components["financials"] = 0

        # ─── 7. LLM success (max 10 pts) ────────────────────
        components["llm"] = round(max(0.0, min(1.0, llm_success_rate)) * 10, 2)

        raw = sum(components.values())
        # Clamp: never claim absolute certainty, never show uselessly low scores
        score = int(max(10, min(98, raw)))

        logger.info(f"Confidence components: {components} → {score}")
        return score

    @staticmethod
    def breakdown(
        *,
        articles: List[Dict[str, Any]],
        events: List[Any],
        competitors: List[Dict[str, Any]],
        sentiment: Dict[str, Any] | None = None,
        financials: Dict[str, Any] | None = None,
        llm_success_rate: float = 1.0,
    ) -> Dict[str, Any]:
        """Return both the score and the component breakdown for display."""
        score = ConfidenceService.compute(
            articles=articles,
            events=events,
            competitors=competitors,
            sentiment=sentiment,
            financials=financials,
            llm_success_rate=llm_success_rate,
        )
        return {
            "score": score,
            "sources": min(20, len(articles) * 1.0),
            "credibility": 0,
            "events": min(20, (len(events) / max(1, len(articles))) * 20),
            "competitors": min(15, len(competitors) * 3.0),
            "sentiment": min(10, len(sentiment or {}) * 1.5),
            "financials": min(10, len(financials or {}) * 2.0),
            "llm": round(max(0.0, min(1.0, llm_success_rate)) * 10, 2),
        }