"""CRUD operations for ResearchRequest."""

import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.database.models.research_request import ResearchRequest
from app.database.schemas.research_schema import ResearchRequestCreate


def create(db: Session, user_id: uuid.UUID, data: ResearchRequestCreate) -> ResearchRequest:
    known = ",".join(data.known_competitors) if data.known_competitors else None
    req = ResearchRequest(
        user_id=user_id,
        company_name=data.company_name.strip(),
        industry=data.industry,
        known_competitors=known,
        research_depth=data.research_depth,
        status="pending",
        progress=0,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def get_by_id(db: Session, request_id: uuid.UUID) -> Optional[ResearchRequest]:
    return db.query(ResearchRequest).filter(ResearchRequest.id == request_id).first()


def list_by_user(
    db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 50
) -> List[ResearchRequest]:
    return (
        db.query(ResearchRequest)
        .filter(ResearchRequest.user_id == user_id)
        .order_by(ResearchRequest.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def list_all(db: Session, skip: int = 0, limit: int = 100) -> List[ResearchRequest]:
    return (
        db.query(ResearchRequest)
        .order_by(ResearchRequest.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_status(
    db: Session,
    request_id: uuid.UUID,
    status: str,
    progress: Optional[int] = None,
    error_message: Optional[str] = None,
) -> Optional[ResearchRequest]:
    req = get_by_id(db, request_id)
    if not req:
        return None
    req.status = status
    if progress is not None:
        req.progress = progress
    if error_message is not None:
        req.error_message = error_message
    db.commit()
    db.refresh(req)
    return req


def delete(db: Session, req: ResearchRequest) -> None:
    db.delete(req)
    db.commit()