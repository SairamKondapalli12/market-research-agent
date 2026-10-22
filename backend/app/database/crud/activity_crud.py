"""CRUD for ActivityLog."""

import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.database.models.activity_log import ActivityLog


def log(
    db: Session,
    action: str,
    actor: str = "System",
    user_id: Optional[uuid.UUID] = None,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    target_label: Optional[str] = None,
    level: str = "info",
    detail: Optional[str] = None,
) -> ActivityLog:
    entry = ActivityLog(
        action=action,
        actor=actor,
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
        target_label=target_label,
        level=level,
        detail=detail,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def list_recent(db: Session, limit: int = 50, user_id: Optional[uuid.UUID] = None) -> List[ActivityLog]:
    q = db.query(ActivityLog)
    if user_id:
        q = q.filter(ActivityLog.user_id == user_id)
    return q.order_by(ActivityLog.created_at.desc()).limit(limit).all()