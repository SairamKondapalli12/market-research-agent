"""Analyst Agent — extracts intelligence events, SWOT, and market trends."""

import json
from typing import Any, Dict, List

from app.agents.base_agent import BaseAgent
from app.agents.prompts.analyst_prompts import SWOT_ANALYSIS_PROMPT, TRENDS_ANALYSIS_PROMPT
from app.agents.tools.event_classifier import EventClassifierTool
from app.agents.tools.significance_scorer import SignificanceScorerTool
from app.database.models.intelligence_event import IntelligenceEvent
from app.database.session import SessionLocal


class AnalystAgent(BaseAgent):
    def __init__(self, llm: Any = None, verbose: bool = False, request_id: str = None):
        super().__init__(
            name="analyst",
            role="Competitive Intelligence Analyst",
            goal="Transform raw articles into structured intelligence.",
            backstory="Former management consultant who specialises in competitive analysis.",
            llm=llm,
            tools=[],
            verbose=verbose,
            request_id=request_id,
        )
        self.classifier = EventClassifierTool()
        self.scorer = SignificanceScorerTool()

    def _extract_events(self, company_name, competitors, articles):
        events: List[Dict[str, Any]] = []
        companies = [company_name] + [c["name"] for c in competitors]

        for idx, article in enumerate(articles):
            if idx % 5 == 0:
                self.log(
                    f"Classifying events from article {idx + 1}/{len(articles)}",
                    progress=50 + int((idx / max(1, len(articles))) * 15),
                )
            text = (article.get("title") or "") + "\n" + (article.get("content") or "")
            if len(text.strip()) < 50:
                continue
            for company in companies:
                if company.lower() not in text.lower():
                    continue
                classified = self.classifier.classify(text, company=company)
                for item in classified:
                    score = self.scorer.score(
                        event_type=item["event_type"],
                        description=item.get("description", ""),
                        company=company,
                    )
                    events.append({
                        "company": company,
                        "event_type": item["event_type"],
                        "title": (article.get("title") or "")[:500],
                        "description": item.get("description", "")[:2000],
                        "significance": score,
                        "source_url": article.get("url"),
                        "event_date": article.get("published_date"),
                    })
        events.sort(key=lambda e: e["significance"], reverse=True)
        return events[:200]

    def _generate_swot(self, company_name, competitors, events):
        swot: Dict[str, Any] = {}
        targets = [{"name": company_name}] + competitors
        for target in targets:
            name = target["name"]
            related = [e for e in events if e["company"] == name]
            summary_lines = "\n".join(
                f"- [{e['event_type']}] {e['title']} (sig={e['significance']})"
                for e in related[:15]
            ) or "(No direct events.)"

            if self.llm is None:
                swot[name] = self._fallback_swot()
                continue

            self.log(f"Building SWOT for {name}", progress=70)
            prompt = SWOT_ANALYSIS_PROMPT.format(company=name, events=summary_lines)
            try:
                response = self.llm.invoke(prompt)
                content = response.content if hasattr(response, "content") else str(response)
                parsed = self._parse_json_block(content)
                swot[name] = parsed or self._fallback_swot()
            except Exception as exc:
                self.log(f"SWOT LLM error: {exc}", level="warning")
                swot[name] = self._fallback_swot()
        return swot

    def _generate_trends(self, company_name, events):
        if self.llm is None:
            return {"trends": ["AI adoption accelerating"]}
        summary_lines = "\n".join(
            f"- [{e['event_type']}] {e['company']}: {e['title']}" for e in events[:40]
        ) or "(No events)"
        self.log("Identifying market trends", progress=75)
        prompt = TRENDS_ANALYSIS_PROMPT.format(company=company_name, events=summary_lines)
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, "content") else str(response)
            parsed = self._parse_json_block(content)
            return parsed or {"trends": []}
        except Exception:
            return {"trends": []}

    @staticmethod
    def _parse_json_block(content: str) -> Dict[str, Any]:
        content = content.strip()
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

    @staticmethod
    def _fallback_swot():
        return {
            "strengths": ["Market presence"],
            "weaknesses": ["Limited public data"],
            "opportunities": ["Product innovation"],
            "threats": ["New entrants"],
        }

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        request_id = inputs["request_id"]
        company_name = inputs["company_name"]
        competitors = inputs.get("competitors", [])
        articles = inputs.get("articles", [])

        try:
            self.log("Extracting intelligence events", progress=52)
            events = self._extract_events(company_name, competitors, articles)
            self.log(f"Extracted {len(events)} events", progress=65)

            swot = self._generate_swot(company_name, competitors, events)
            trends = self._generate_trends(company_name, events)

            db = SessionLocal()
            try:
                for e in events:
                    db.add(IntelligenceEvent(
                        request_id=request_id,
                        company=e["company"],
                        event_type=e["event_type"],
                        title=e["title"],
                        description=e["description"],
                        significance=e["significance"],
                        source_url=e["source_url"],
                        event_date=e["event_date"],
                    ))
                db.commit()
            finally:
                db.close()

            return {"success": True, "events": events, "swot": swot, "trends": trends, "error": None}
        except Exception as exc:
            self.log(f"Analyst failed: {exc}", level="error")
            return {"success": False, "events": [], "swot": {}, "trends": {}, "error": str(exc)}