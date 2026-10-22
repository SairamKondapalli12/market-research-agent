"""Celery worker for scheduled monitoring of watchlisted companies."""

from app.config.logging_config import get_logger
from app.services.monitoring_service import MonitoringService
from app.workers.celery_app import celery_app


logger = get_logger(__name__)


@celery_app.task(name="app.workers.monitoring_worker.check_watchlist")
def check_watchlist():
    """Iterate through watchlist items and trigger research when due."""
    logger.info("[Celery] Checking watchlist for due items...")
    due = MonitoringService.list_due_watchlist_items()
    logger.info(f"[Celery] {len(due)} watchlist items are due.")

    triggered = []
    for item in due:
        try:
            request_id = MonitoringService.trigger_research_for_watchlist(str(item.id))
            triggered.append({"watchlist_id": str(item.id), "request_id": request_id})
        except Exception as exc:
            logger.error(f"[Celery] Failed for watchlist {item.id}: {exc}")

    return {"triggered": triggered, "count": len(triggered)}