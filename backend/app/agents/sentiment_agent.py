"""Sentiment Agent — scores market sentiment per competitor."""

import json
from typing import Any, Dict, List

from app.agents.base_agent import BaseAgent
from app.agents.prompts.sentiment_prompts import (
    SENTIMENT_AGGREGATE_PROMPT,
    SENTIMENT_ANALYSIS_PROMPT,
)
from app.agents.tools.sentiment_scorer import SentimentScorerTool
from app.config.logging_config import get_logger
from app.database.crud import sentiment_crud
from app.database.session import SessionLocal

logger = get_logger(__name__)


class SentimentAgent(BaseAgent):
    """Analyzes sentiment across all gathered articles for each competitor."""

    MAX_ARTICLES_PER_COMPANY = 8

    def __init__(self, llm: Any = None, verbose: bool = False, request_id: str = None):
        super().__init__(
            name="sentiment",
            role="Market Sentiment Analyst",
            goal="Quantify how each competitor is being perceived across media and news.",
            backstory=(
                "You are a former equity research analyst specialising in "
                "textual sentiment signals. You have calibrated hundreds of "
                "sentiment models against real market outcomes."
            ),
            llm=llm,
            tools=[],
            verbose=verbose,
            request_id=request_id,
        )
        self.fallback = SentimentScorerTool()

    @staticmethod
    def _parse_json(content: str) -> Dict[str, Any]:
        content = (content or "").strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:]
        s, e = content.find("{"), content.rfind("}")
        if s == -1 or e == -1:
            return {}
        try:
            return json.loads(content[s : e + 1])
        except json.JSONDecodeError:
            return {}

    def _llm_score(self, company: str, text: str) -> Dict[str, Any]:
        if self.llm is None:
            return self.fallback.score(text)
        prompt = SENTIMENT_ANALYSIS_PROMPT.format(company=company, text=text[:4000])
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, "content") else str(response)
            parsed = self._parse_json(content)
            if "score" not in parsed:
                return self.fallback.score(text)
            parsed["score"] = max(-1.0, min(1.0, float(parsed["score"])))
            parsed.setdefault("label", "neutral")
            parsed.setdefault("rationale", "")
            return parsed
        except Exception as exc:
            logger.warning(f"Sentiment LLM error for {company}: {exc}")
            return self.fallback.score(text)

    def _articles_for_company(
        self, company: str, articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        needle = company.lower()
        return [
            a for a in articles
            if needle in ((a.get("title") or "") + (a.get("content") or "")).lower()
        ][: self.MAX_ARTICLES_PER_COMPANY]

    def _aggregate(
        self, company: str, per_article: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if not per_article:
            return {
                "overall_score": 0.0,
                "overall_label": "neutral",
                "distribution": {"positive": 0, "neutral": 0, "negative": 0},
                "drivers": [],
                "summary": "No articles available for sentiment analysis.",
            }

        scores = [float(x.get("score", 0.0)) for x in per_article]
        avg = sum(scores) / len(scores)

        dist = {"positive": 0, "neutral": 0, "negative": 0}
        for s in scores:
            if s > 0.15:
                dist["positive"] += 1
            elif s < -0.15:
                dist["negative"] += 1
            else:
                dist["neutral"] += 1

        if avg > 0.15:
            label = "positive"
        elif avg < -0.15:
            label = "negative"
        else:
            label = "neutral"

        # Ask LLM for narrative + drivers if available
        if self.llm is not None:
            items = "\n".join(
                f"- score={x['score']:.2f} label={x['label']} rationale={x.get('rationale','')}"
                for x in per_article
            )
            prompt = SENTIMENT_AGGREGATE_PROMPT.format(company=company, items=items)
            try:
                response = self.llm.invoke(prompt)
                content = response.content if hasattr(response, "content") else str(response)
                parsed = self._parse_json(content)
                if parsed:
                    parsed.setdefault("overall_score", round(avg, 3))
                    parsed.setdefault("overall_label", label)
                    parsed.setdefault("distribution", dist)
                    parsed.setdefault("drivers", [])
                    parsed.setdefault("summary", "")
                    return parsed
            except Exception as exc:
                logger.warning(f"Sentiment aggregate LLM error: {exc}")

        return {
            "overall_score": round(avg, 3),
            "overall_label": label,
            "distribution": dist,
            "drivers": [],
            "summary": f"Aggregate sentiment across {len(scores)} articles: {label}.",
        }

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        request_id = inputs["request_id"]
        company_name = inputs["company_name"]
        competitors = inputs.get("competitors", [])
        articles = inputs.get("articles", [])

        self.log("Analyzing market sentiment", progress=78)

        try:
            targets = [company_name] + [c["name"] for c in competitors]
            results: Dict[str, Any] = {}

            for target in targets:
                target_articles = self._articles_for_company(target, articles)
                self.log(f"Scoring {len(target_articles)} articles for {target}", progress=80)

                per_article: List[Dict[str, Any]] = []
                for a in target_articles:
                    text = (a.get("title") or "") + "\n" + (a.get("content") or "")
                    if len(text.strip()) < 40:
                        continue
                    result = self._llm_score(target, text)
                    per_article.append({
                        "url": a.get("url"),
                        "title": a.get("title"),
                        "score": result.get("score", 0.0),
                        "label": result.get("label", "neutral"),
                        "rationale": result.get("rationale", ""),
                    })

                aggregate = self._aggregate(target, per_article)
                results[target] = {
                    "articles": per_article,
                    "overall_score": aggregate.get("overall_score", 0.0),
                    "overall_label": aggregate.get("overall_label", "neutral"),
                    "distribution": aggregate.get("distribution", {}),
                    "drivers": aggregate.get("drivers", []),
                    "summary": aggregate.get("summary", ""),
                }

            # Persist
            db = SessionLocal()
            try:
                for company, data in results.items():
                    sentiment_crud.create(
                        db,
                        request_id=request_id,
                        company=company,
                        score=data["overall_score"],
                        label=data["overall_label"],
                        distribution=data["distribution"],
                        drivers=data["drivers"],
                        summary=data["summary"],
                        articles=data["articles"],
                    )
            finally:
                db.close()

            self.log("Sentiment analysis complete", progress=80)
            return {"success": True, "sentiment": results, "error": None}

        except Exception as exc:
            self.log(f"Sentiment agent failed: {exc}", level="error")
            return {"success": False, "sentiment": {}, "error": str(exc)}