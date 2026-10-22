"""Executive One-Pager generation service."""

import json
from typing import Any, Dict

from app.agents.prompts.onepager_prompts import ONEPAGER_PROMPT
from app.config.logging_config import get_logger
from app.config.settings import settings
from app.database.crud import report_crud
from app.database.models.report import Report

logger = get_logger(__name__)


class OnePagerService:

    @staticmethod
    def _llm():
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.startswith("your-"):
            return None
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.2,
                max_output_tokens=8192,
                timeout=60,
                convert_system_message_to_human=True,
            )
        except Exception as exc:
            logger.error(f"One-pager LLM init failed: {exc}")
            return None

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

    @staticmethod
    def _fallback(report: Report) -> Dict[str, Any]:
        """Deterministic fallback when LLM is unavailable."""
        events = []
        recs = (report.recommendations or {}).get("recommendations", [])[:3]
        # Use executive summary as bullet 1, rest as key points
        points = []
        if report.executive_summary:
            points.append(report.executive_summary.split(".")[0].strip()[:120] + ".")

        # Derive from swot
        swot = report.swot_analysis or {}
        for company, data in list(swot.items())[:2]:
            threats = (data.get("threats") or [])[:1]
            if threats:
                points.append(f"{company}: {threats[0][:100]}")

        while len(points) < 3 and len(recs) > 0:
            points.append(recs.pop(0)[:120])

        return {
            "headline": f"Key insights on {report.title.split(':')[-1].strip()}",
            "key_points": points[:5] or ["No summary available."],
            "action": recs[0][:120] if recs else "Review the full report for details.",
        }

    @staticmethod
    def generate(report_id) -> Dict[str, Any]:
        from app.database.session import SessionLocal

        db = SessionLocal()
        try:
            report = report_crud.get_by_id(db, report_id)
            if not report:
                raise ValueError("Report not found")

            events = (report.recommendations or {}).get("top_events") or []
            # Fall back to intelligence events if the report doesn't store top events
            if not events:
                from app.database.models.intelligence_event import IntelligenceEvent
                rows = (
                    db.query(IntelligenceEvent)
                    .filter(IntelligenceEvent.request_id == report.request_id)
                    .order_by(IntelligenceEvent.significance.desc())
                    .limit(3)
                    .all()
                )
                events = [f"[{e.event_type}] {e.company}: {e.title}" for e in rows]

            recs = (report.recommendations or {}).get("recommendations", [])[:3]

            llm = OnePagerService._llm()
            if llm is None:
                return OnePagerService._fallback(report)

            prompt = ONEPAGER_PROMPT.format(
                company=report.title.split(":")[-1].strip(),
                title=report.title,
                executive_summary=report.executive_summary or "(none)",
                events="\n".join(f"- {e}" for e in events),
                recommendations="\n".join(f"- {r}" for r in recs),
            )
            try:
                response = llm.invoke(prompt)
                content = response.content if hasattr(response, "content") else str(response)
                parsed = OnePagerService._parse_json(content)
                if not parsed:
                    return OnePagerService._fallback(report)
                parsed.setdefault("headline", "")
                parsed.setdefault("key_points", [])
                parsed.setdefault("action", "")
                return parsed
            except Exception as exc:
                logger.warning(f"One-pager LLM error: {exc}")
                return OnePagerService._fallback(report)
        finally:
            db.close()