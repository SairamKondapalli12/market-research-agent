"""FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.logging_config import get_logger, setup_logging
from app.config.settings import settings
from app.database.base import Base
from app.database.session import engine

from app.database import models  # noqa: F401 — register models

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    if not settings.is_production:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ensured (dev mode).")

    yield

    logger.info("Shutting down…")
    engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Autonomous AI-Powered Market Research Agent API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        logger.error(f"Health DB error: {exc}")
        db_status = "disconnected"
    return {"status": "ok", "database": db_status, "environment": settings.ENVIRONMENT}


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.exception(f"Unhandled: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ─── Routers ───────────────────────────────────────────────────
from app.api.routes import (
    activity,
    admin,
    analytics,
    auth,
    chat,
    competitors,
    diffs,
    intelligence_feed,
    notifications,
    onepager,
    reports,
    research,
    schedules,
    settings as settings_routes,
    share,
    watchlist,
    ws,
    compare,
)

P = settings.API_V1_PREFIX

app.include_router(auth.router, prefix=f"{P}/auth", tags=["Auth"])
app.include_router(research.router, prefix=f"{P}/research", tags=["Research"])
app.include_router(reports.router, prefix=f"{P}/reports", tags=["Reports"])
app.include_router(competitors.router, prefix=f"{P}/competitors", tags=["Competitors"])
app.include_router(watchlist.router, prefix=f"{P}/watchlist", tags=["Watchlist"])
app.include_router(intelligence_feed.router, prefix=f"{P}/feed", tags=["Feed"])
app.include_router(settings_routes.router, prefix=f"{P}/settings", tags=["Settings"])
app.include_router(notifications.router, prefix=f"{P}/notifications", tags=["Notifications"])
app.include_router(analytics.router, prefix=f"{P}/analytics", tags=["Analytics"])
app.include_router(activity.router, prefix=f"{P}/activity", tags=["Activity"])
app.include_router(share.router, prefix=f"{P}/share", tags=["Share"])
app.include_router(admin.router, prefix=f"{P}/admin", tags=["Admin"])
app.include_router(compare.router, prefix=f"{P}/compare", tags=["Compare"])

# ─── Feature expansion ────────────────────────────────────────
app.include_router(chat.router, prefix=f"{P}/chat", tags=["Chat"])
app.include_router(schedules.router, prefix=f"{P}/schedules", tags=["Schedules"])
app.include_router(diffs.router, prefix=f"{P}/diffs", tags=["Diffs"])
app.include_router(onepager.router, prefix=f"{P}/onepager", tags=["One-Pager"])

# WebSocket lives outside /api/v1
app.include_router(ws.router, prefix="/ws", tags=["WebSocket"])