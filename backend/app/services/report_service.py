"""Report service — retrieval and export helpers."""

import uuid
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.database.crud import report_crud, research_crud
from app.database.models.report import Report


class ReportService:

    @staticmethod
    def get_report_for_user(
        db: Session, report_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Report]:
        report = report_crud.get_by_id(db, report_id)
        if not report:
            return None
        parent = research_crud.get_by_id(db, report.request_id)
        if not parent or parent.user_id != user_id:
            return None
        return report

    @staticmethod
    def to_export_dict(report: Report) -> Dict[str, Any]:
        return {
            "id": str(report.id),
            "title": report.title,
            "executive_summary": report.executive_summary,
            "report_content": report.report_content,
            "swot_analysis": report.swot_analysis,
            "trends": report.trends,
            "recommendations": report.recommendations,
            "confidence_score": report.confidence_score,
            "sentiment_summary": report.sentiment_summary,
            "financial_summary": report.financial_summary,
            "diff_significance": report.diff_significance,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }