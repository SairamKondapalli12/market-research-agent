"""Notification routes."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.crud import notification_crud
from app.database.models.user import User
from app.database.schemas.notification_schema import NotificationRead
from app.database.session import get_db

router = APIRouter()


@router.get("", response_model=List[NotificationRead])
def list_notifications(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    return notification_crud.list_for_user(db, current.id)


@router.post("/{notification_id}/read", response_model=NotificationRead)
def mark_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    import uuid
    n = notification_crud.mark_read(db, uuid.UUID(notification_id), current.id)
    return n


@router.post("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    count = notification_crud.mark_all_read(db, current.id)
    return {"marked": count}