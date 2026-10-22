"""CRUD for ReportDiff."""

import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.database.models.report_diff import ReportDiff


def create(
    db: Session,
    current_report_id: uuid.UUID,
    previous_report_id: uuid.UUID,
    request_id: uuid.UUID,
    company_name: str,
    significance: int,
    summary: str,
    payload: Dict[str, Any],
) -> ReportDiff:
    diff = ReportDiff(
        current_report_id=current_report_id,
        previous_report_id=previous_report_id,
        request_id=request_id,
        company_name=company_name,
        significance=significance,
        summary=summary,
        payload=payload,
    )
    db.add(diff)
    db.commit()
    db.refresh(diff)
    return diff


def get_by_current_report(db: Session, report_id: uuid.UUID) -> Optional[ReportDiff]:
    return (
        db.query(ReportDiff)
        .filter(ReportDiff.current_report_id == report_id)
        .order_by(ReportDiff.created_at.desc())
        .first()
    )


def list_by_company(db: Session, company_name: str, limit: int = 20) -> List[ReportDiff]:
    return (
        db.query(ReportDiff)
        .filter(ReportDiff.company_name == company_name)
        .order_by(ReportDiff.created_at.desc())
        .limit(limit)
        .all()
    )