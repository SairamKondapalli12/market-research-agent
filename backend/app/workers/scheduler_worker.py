"""Celery worker — runs due research schedules."""

from app.config.logging_config import get_logger
from app.database.crud import research_crud, schedule_crud
from app.database.schemas.research_schema import ResearchRequestCreate
from app.database.session import SessionLocal
from app.services.research_service import ResearchService
from app.services.schedule_service import ScheduleService
from app.workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="app.workers.scheduler_worker.tick")
def tick():
    """Find due schedules and trigger a research run for each."""
    due = ScheduleService.list_due()
    logger.info(f"[Scheduler] {len(due)} schedule(s) due")

    triggered = []
    for sched in due:
        db = SessionLocal()
        try:
            payload = ResearchRequestCreate(
                company_name=sched.company_name,
                industry=sched.industry,
                research_depth=sched.research_depth,
            )
            req = research_crud.create(db, user_id=sched.user_id, data=payload)
            schedule_crud.mark_ran(db, sched, req.id)

            service = ResearchService()
            service.run_pipeline(request_id=str(req.id), user_id=str(sched.user_id))

            triggered.append({"schedule_id": str(sched.id), "request_id": str(req.id)})
        except Exception as exc:
            logger.error(f"[Scheduler] failed for {sched.id}: {exc}")
        finally:
            db.close()

    return {"triggered": triggered, "count": len(triggered)}