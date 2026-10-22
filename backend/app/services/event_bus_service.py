"""Redis pub/sub event bus for real-time agent log streaming."""

import json
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

import redis

from app.config.logging_config import get_logger
from app.config.settings import settings

logger = get_logger(__name__)


_sync_client: Optional[redis.Redis] = None


def _get_sync_client() -> redis.Redis:
    global _sync_client
    if _sync_client is None:
        _sync_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _sync_client


def channel_name(request_id: UUID | str) -> str:
    return f"research:{request_id}:events"


def publish_event(
    request_id: UUID | str,
    agent: str,
    message: str,
    level: str = "info",
    progress: Optional[int] = None,
) -> None:
    """Publish an agent log event to Redis."""
    payload = {
        "agent": agent,
        "level": level,
        "message": message,
        "progress": progress,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        client = _get_sync_client()
        client.publish(channel_name(request_id), json.dumps(payload))
    except Exception as exc:
        logger.warning(f"event_bus publish failed: {exc}")