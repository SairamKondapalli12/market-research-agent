"""CRUD for SentimentRecord."""

import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.database.models.sentiment_record import SentimentRecord


def create(
    db: Session,
    request_id: uuid.UUID,
    company: str,
    score: float,
    label: str,
    distribution: Optional[Dict[str, Any]] = None,
    drivers: Optional[List[str]] = None,
    summary: Optional[str] = None,
    articles: Optional[List[Dict[str, Any]]] = None,
) -> SentimentRecord:
    record = SentimentRecord(
        request_id=request_id,
        company=company,
        score=score,
        label=label,
        distribution=distribution,
        drivers=drivers,
        summary=summary,
        articles=articles,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_by_request(db: Session, request_id: uuid.UUID) -> List[SentimentRecord]:
    return (
        db.query(SentimentRecord)
        .filter(SentimentRecord.request_id == request_id)
        .order_by(SentimentRecord.score.desc())
        .all()
    )