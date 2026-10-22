"""Celery worker for research tasks."""

from app.config.logging_config import get_logger
from app.database.crud import report_crud
from app.database.session import SessionLocal
from app.services.change_detection_service import ChangeDetectionService
from app.services.research_service import ResearchService
from app.workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="app.workers.research_worker.run_research", bind=True, max_retries=2)
def run_research(self, request_id: str, user_id: str):
    logger.info(f"[Celery] Running research for request={request_id}")
    try:
        service = ResearchService()
        result = service.run_pipeline(request_id=request_id, user_id=user_id)

        if result.get("success") and result.get("report"):
            # Trigger change detection for the newly generated report
            try:
                report_id = result["report"]["id"]
                ChangeDetectionService.detect(report_id)
            except Exception as exc:
                logger.warning(f"Change detection failed: {exc}")

        return result
    except Exception as exc:
        logger.error(f"[Celery] Research failed: {exc}")
        raise self.retry(exc=exc, countdown=60)