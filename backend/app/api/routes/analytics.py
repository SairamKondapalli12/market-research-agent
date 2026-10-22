"""Analytics routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.models.user import User
from app.database.session import get_db
from app.services import analytics_service

router = APIRouter()


@router.get("/summary")
def summary(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    return analytics_service.summary(db, current.id)


@router.get("/research-over-time")
def research_over_time(
    days: int = 14,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    return analytics_service.research_over_time(db, current.id, days=days)