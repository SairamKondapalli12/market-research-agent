"""Activity log routes."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.crud import activity_crud
from app.database.models.user import User
from app.database.schemas.activity_schema import ActivityRead
from app.database.session import get_db

router = APIRouter()


@router.get("", response_model=List[ActivityRead])
def list_activity(
    limit: int = 50,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    return activity_crud.list_recent(db, limit=limit, user_id=current.id)