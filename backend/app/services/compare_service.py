"""Compare two reports side-by-side."""

import uuid
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.config.logging_config import get_logger
from app.database.crud import report_crud, research_crud

logger = get_logger(__name__)


class CompareService:

    @staticmethod
    def _event_summary(report) -> List[Dict[str, Any]]:
        events = (report.recommendations or {}).get("top_events") or []
        if events:
            return events[:5]
        # Fallback: read from DB
        try:
            from app.database.models.intelligence_event import IntelligenceEvent
            db = None
            return []
        except Exception:
            return []

    @staticmethod
    def _extract_competitors(report) -> List[str]:
        swot = report.swot_analysis or {}
        return sorted(list(swot.keys()))

    @staticmethod
    def _extract_recommendations(report) -> List[str]:
        return [
            r.strip()
            for r in (report.recommendations or {}).get("recommendations", [])
            if r
        ]

    @staticmethod
    def _extract_sentiment(report) -> Dict[str, Any] | None:
        s = report.sentiment_summary
        if not s or not isinstance(s, dict):
            return None
        out = {}
        for company, data in s.items():
            out[company] = {
                "score": data.get("overall_score", 0),
                "label": data.get("overall_label", "neutral"),
            }
        return out

    @staticmethod
    def _extract_financials(report) -> Dict[str, Any] | None:
        f = report.financial_summary
        if not f or not isinstance(f, dict):
            return None
        out = {}
        for company, data in f.items():
            out[company] = {
                "total_raised": data.get("total_raised"),
                "valuation": data.get("latest_valuation"),
            }
        return out

    @staticmethod
    def _build_item(db: Session, report) -> Dict[str, Any]:
        req = research_crud.get_by_id(db, report.request_id)
        company_name = req.company_name if req else (report.title.split(":")[-1].strip() if report.title else "Unknown")
        return {
            "id": report.id,
            "title": report.title,
            "company_name": company_name,
            "created_at": report.created_at.isoformat() if report.created_at else "",
            "confidence_score": report.confidence_score,
            "executive_summary": report.executive_summary,
            "competitors": CompareService._extract_competitors(report),
            "top_events": CompareService._event_summary(report),
            "recommendations": CompareService._extract_recommendations(report),
            "sentiment": CompareService._extract_sentiment(report),
            "financials": CompareService._extract_financials(report),
        }

    @staticmethod
    def compare(db: Session, left_id: uuid.UUID, right_id: uuid.UUID) -> Dict[str, Any]:
        left = report_crud.get_by_id(db, left_id)
        right = report_crud.get_by_id(db, right_id)
        if not left or not right:
            raise ValueError("One or both reports not found")

        left_item = CompareService._build_item(db, left)
        right_item = CompareService._build_item(db, right)

        left_comps = set(left_item["competitors"])
        right_comps = set(right_item["competitors"])
        left_recs = set(left_item["recommendations"])
        right_recs = set(right_item["recommendations"])

        return {
            "left": left_item,
            "right": right_item,
            "added_competitors": sorted(right_comps - left_comps),
            "removed_competitors": sorted(left_comps - right_comps),
            "common_competitors": sorted(left_comps & right_comps),
            "new_recommendations": sorted(right_recs - left_recs),
            "dropped_recommendations": sorted(left_recs - right_recs),
            "common_recommendations": sorted(left_recs & right_recs),
        }