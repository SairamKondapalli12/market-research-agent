"""Activity log helper."""

from typing import Optional
from uuid import UUID

from app.config.logging_config import get_logger
from app.database.crud import activity_crud
from app.database.session import SessionLocal

logger = get_logger(__name__)


def record(
    action: str,
    actor: str = "System",
    user_id: Optional[UUID] = None,
    target_type: Optional[str] = None,
    target_id: Optional[str] = None,
    target_label: Optional[str] = None,
    level: str = "info",
    detail: Optional[str] = None,
) -> None:
    """Write an activity log entry (non-blocking)."""
    db = SessionLocal()
    try:
        activity_crud.log(
            db,
            action=action,
            actor=actor,
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            target_label=target_label,
            level=level,
            detail=detail,
        )
    except Exception as exc:
        logger.warning(f"Failed to record activity: {exc}")
    finally:
        db.close()