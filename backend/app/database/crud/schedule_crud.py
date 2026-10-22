"""CRUD for ResearchSchedule."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.database.models.research_schedule import ResearchSchedule
from app.database.schemas.schedule_schema import ScheduleCreate


def _compute_next(frequency: str, from_dt: Optional[datetime] = None) -> str:
    base = from_dt or datetime.now(timezone.utc)
    if frequency == "daily":
        nxt = base + timedelta(days=1)
    elif frequency == "monthly":
        nxt = base + timedelta(days=30)
    else:  # weekly
        nxt = base + timedelta(days=7)
    return nxt.isoformat()


def create(db: Session, user_id: uuid.UUID, payload: ScheduleCreate) -> ResearchSchedule:
    sched = ResearchSchedule(
        user_id=user_id,
        company_name=payload.company_name,
        industry=payload.industry,
        research_depth=payload.research_depth,
        frequency=payload.frequency,
        next_run_at=_compute_next(payload.frequency),
        notes=payload.notes,
    )
    db.add(sched)
    db.commit()
    db.refresh(sched)
    return sched


def list_for_user(db: Session, user_id: uuid.UUID) -> List[ResearchSchedule]:
    return (
        db.query(ResearchSchedule)
        .filter(ResearchSchedule.user_id == user_id)
        .order_by(ResearchSchedule.created_at.desc())
        .all()
    )


def get_by_id(db: Session, schedule_id: uuid.UUID) -> Optional[ResearchSchedule]:
    return db.query(ResearchSchedule).filter(ResearchSchedule.id == schedule_id).first()


def update(db: Session, sched: ResearchSchedule, **fields) -> ResearchSchedule:
    for k, v in fields.items():
        if v is not None and hasattr(sched, k):
            setattr(sched, k, v)
    if "frequency" in fields and fields["frequency"]:
        sched.next_run_at = _compute_next(sched.frequency)
    db.commit()
    db.refresh(sched)
    return sched


def mark_ran(
    db: Session, sched: ResearchSchedule, request_id: uuid.UUID
) -> ResearchSchedule:
    sched.last_run_at = datetime.now(timezone.utc).isoformat()
    sched.next_run_at = _compute_next(sched.frequency)
    sched.runs_completed += 1
    sched.last_request_id = request_id
    db.commit()
    db.refresh(sched)
    return sched


def delete(db: Session, sched: ResearchSchedule) -> None:
    db.delete(sched)
    db.commit()