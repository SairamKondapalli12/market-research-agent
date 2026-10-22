"""Admin console routes (superuser only)."""

import shutil
import time
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_current_superuser
from app.database.models.user import User
from app.database.schemas.admin_schema import (
    AdminUserRead,
    SystemHealth,
    AdminOverview,
)
from app.database.session import get_db
from app.services.analytics_service import system_health as system_health_svc
from app.config.settings import settings

router = APIRouter()


@router.get("/users", response_model=List[AdminUserRead])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_superuser),
):
    if user_id == current.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()


@router.patch("/users/{user_id}/toggle-active", response_model=AdminUserRead)
def toggle_active(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user


@router.get("/system", response_model=SystemHealth)
def system_health(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    # DB check
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"

    # Redis check
    redis_status = "connected"
    try:
        import redis as redis_lib

        r = redis_lib.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        r.ping()
    except Exception:
        redis_status = "disconnected"

    stats = system_health_svc(db)

    # Disk usage (of the current working dir — good enough for a demo)
    try:
        usage = shutil.disk_usage(".")
        storage_used_gb = round(usage.used / (1024**3), 1)
        storage_total_gb = round(usage.total / (1024**3), 1)
        storage_percent = int((usage.used / usage.total) * 100)
    except Exception:
        storage_used_gb = 0
        storage_total_gb = 0
        storage_percent = 0

    return SystemHealth(
        database=db_status,
        redis=redis_status,
        pipeline="operational",
        api="operational",
        storage_used=f"{storage_used_gb} GB",
        storage_total=f"{storage_total_gb} GB",
        storage_percent=storage_percent,
        total_users=stats["total_users"],
        active_users=stats["active_users"],
        total_reports=stats["total_reports"],
        total_research=stats["total_research"],
    )


@router.get("/overview", response_model=AdminOverview)
def overview(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    start = time.time()
    # Ping the DB to measure latency
    db.execute(text("SELECT 1"))
    latency_ms = int((time.time() - start) * 1000)

    stats = system_health_svc(db)
    return AdminOverview(
        total_users=stats["total_users"],
        active_sessions=stats["active_users"],
        queue_depth=0,
        api_latency_ms=latency_ms,
    )