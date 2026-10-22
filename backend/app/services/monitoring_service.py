"""Monitoring service — recurring research runs for watchlisted companies."""

from datetime import datetime, timezone
from typing import List

from app.config.logging_config import get_logger
from app.database.crud import research_crud
from app.database.models.watchlist import Watchlist
from app.database.schemas.research_schema import ResearchRequestCreate
from app.database.session import SessionLocal
from app.services.research_service import ResearchService


logger = get_logger(__name__)


class MonitoringService:
    """Runs periodic research on watchlisted companies and raises alerts."""

    @staticmethod
    def list_due_watchlist_items() -> List[Watchlist]:
        """Return watchlist items that are due for a check."""
        db = SessionLocal()
        try:
            items = db.query(Watchlist).filter(Watchlist.is_active.is_(True)).all()
            now = datetime.now(timezone.utc)
            due: List[Watchlist] = []
            for item in items:
                if not item.last_checked:
                    due.append(item)
                    continue
                try:
                    last = datetime.fromisoformat(item.last_checked)
                except Exception:
                    due.append(item)
                    continue

                delta_hours = (now - last).total_seconds() / 3600
                if item.monitoring_frequency == "daily" and delta_hours >= 24:
                    due.append(item)
                elif item.monitoring_frequency == "weekly" and delta_hours >= 24 * 7:
                    due.append(item)
                elif item.monitoring_frequency == "monthly" and delta_hours >= 24 * 30:
                    due.append(item)
            return due
        finally:
            db.close()

    @staticmethod
    def trigger_research_for_watchlist(item_id: str) -> str:
        """Create a research request for a watchlisted company and run it."""
        db = SessionLocal()
        try:
            item = db.query(Watchlist).filter(Watchlist.id == item_id).first()
            if not item:
                raise ValueError("Watchlist item not found")

            payload = ResearchRequestCreate(
                company_name=item.company_name, research_depth="standard"
            )
            req = research_crud.create(db, user_id=item.user_id, data=payload)

            # Mark watchlist item as checked
            item.last_checked = datetime.now(timezone.utc).isoformat()
            db.commit()

            request_id = str(req.id)
        finally:
            db.close()

        # Run the pipeline synchronously (in production this is a Celery task)
        service = ResearchService()
        service.run_pipeline(request_id=request_id, user_id="system")
        return request_id