"""Celery application configuration."""

from celery import Celery
from celery.schedules import crontab

from app.config.settings import settings


celery_app = Celery(
    "market_research",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=60 * 30,
    task_soft_time_limit=60 * 25,
    worker_max_tasks_per_child=50,
    broker_connection_retry_on_startup=True,
)

# Import tasks so Celery registers them
from app.workers import (  # noqa: E402,F401
    research_worker,
    monitoring_worker,
    scheduler_worker,
)

# ─── Beat schedule ─────────────────────────────────────────────
celery_app.conf.beat_schedule = {
    "check-watchlist-every-hour": {
        "task": "app.workers.monitoring_worker.check_watchlist",
        "schedule": crontab(minute=0),
    },
    "tick-research-schedules": {
        "task": "app.workers.scheduler_worker.tick",
        "schedule": crontab(minute="*/5"),
    },
}