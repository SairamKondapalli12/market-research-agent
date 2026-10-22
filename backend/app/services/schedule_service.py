"""Scheduling service — determines which schedules are due."""

from datetime import datetime, timezone
from typing import List

from app.config.logging_config import get_logger
from app.database.models.research_schedule import ResearchSchedule
from app.database.session import SessionLocal

logger = get_logger(__name__)


class ScheduleService:

    @staticmethod
    def list_due() -> List[ResearchSchedule]:
        db = SessionLocal()
        try:
            items = (
                db.query(ResearchSchedule)
                .filter(ResearchSchedule.is_active.is_(True))
                .all()
            )
            now = datetime.now(timezone.utc)
            due: List[ResearchSchedule] = []
            for s in items:
                if not s.next_run_at:
                    due.append(s)
                    continue
                try:
                    nxt = datetime.fromisoformat(s.next_run_at)
                    if nxt.tzinfo is None:
                        nxt = nxt.replace(tzinfo=timezone.utc)
                    if now >= nxt:
                        due.append(s)
                except Exception:
                    due.append(s)
            return due
        finally:
            db.close()