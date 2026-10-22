"""WebSocket endpoint for real-time agent log streaming."""

from typing import List

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config.logging_config import get_logger
from app.config.settings import settings
from app.database.models.agent_log_event import AgentLogEvent
from app.database.session import SessionLocal
from app.services.event_bus_service import channel_name

logger = get_logger(__name__)

router = APIRouter()


def _client_still_connected(websocket: WebSocket) -> bool:
    """Return True if the WebSocket client is still connected."""
    try:
        return websocket.client_state.name == "CONNECTED"
    except Exception:
        return False


@router.websocket("/research/{request_id}")
async def research_log_stream(websocket: WebSocket, request_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connected for request {request_id}")

    # ─── 1. Replay persisted events from DB ───────────────
    db = SessionLocal()
    try:
        history: List[AgentLogEvent] = (
            db.query(AgentLogEvent)
            .filter(AgentLogEvent.request_id == request_id)
            .order_by(AgentLogEvent.sequence.asc())
            .all()
        )
        logger.info(f"Sending {len(history)} historical events")
        for ev in history:
            if not _client_still_connected(websocket):
                break
            try:
                await websocket.send_json({
                    "agent": ev.agent,
                    "level": ev.level,
                    "message": ev.message,
                    "progress": ev.progress,
                    "timestamp": ev.created_at.isoformat() if ev.created_at else None,
                    "historical": True,
                })
            except (WebSocketDisconnect, RuntimeError):
                break
    except Exception as exc:
        logger.warning(f"Failed to send historical events: {exc}")
    finally:
        db.close()

    # ─── 2. Subscribe to live Redis channel ───────────────
    client = None
    pubsub = None
    try:
        client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        pubsub = client.pubsub()
        await pubsub.subscribe(channel_name(request_id))

        async for message in pubsub.listen():
            if message.get("type") != "message":
                continue

            # Guard: stop sending if the client disconnected
            if not _client_still_connected(websocket):
                logger.info(f"Client disconnected mid-stream for {request_id}")
                break

            try:
                await websocket.send_text(message["data"])
            except (WebSocketDisconnect, RuntimeError):
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for request {request_id}")
    except Exception as exc:
        logger.warning(f"WebSocket error: {exc}")
    finally:
        try:
            if pubsub:
                await pubsub.unsubscribe(channel_name(request_id))
                await pubsub.close()
        except Exception:
            pass
        try:
            if client:
                await client.close()
        except Exception:
            pass