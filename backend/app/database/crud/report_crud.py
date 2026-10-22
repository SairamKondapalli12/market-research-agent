"""CRUD operations for Report."""

import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.database.models.report import Report


def create(
    db: Session,
    request_id: uuid.UUID,
    title: str,
    executive_summary: Optional[str] = None,
    report_content: Optional[str] = None,
    swot_analysis: Optional[Dict[str, Any]] = None,
    trends: Optional[Dict[str, Any]] = None,
    recommendations: Optional[Dict[str, Any]] = None,
    confidence_score: Optional[int] = None,
) -> Report:
    report = Report(
        request_id=request_id,
        title=title,
        executive_summary=executive_summary,
        report_content=report_content,
        swot_analysis=swot_analysis,
        trends=trends,
        recommendations=recommendations,
        confidence_score=confidence_score,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_by_id(db: Session, report_id: uuid.UUID) -> Optional[Report]:
    return db.query(Report).filter(Report.id == report_id).first()


def get_by_request(db: Session, request_id: uuid.UUID) -> Optional[Report]:
    return (
        db.query(Report)
        .filter(Report.request_id == request_id)
        .order_by(Report.created_at.desc())
        .first()
    )


def list_by_request(db: Session, request_id: uuid.UUID) -> List[Report]:
    return (
        db.query(Report)
        .filter(Report.request_id == request_id)
        .order_by(Report.created_at.desc())
        .all()
    )


def delete(db: Session, report: Report) -> None:
    db.delete(report)
    db.commit()