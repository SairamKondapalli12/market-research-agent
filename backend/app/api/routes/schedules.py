"""Research schedule routes."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.crud import schedule_crud
from app.database.models.user import User
from app.database.schemas.schedule_schema import (
    ScheduleCreate,
    ScheduleRead,
    ScheduleUpdate,
)
from app.database.session import get_db

router = APIRouter()


@router.get("", response_model=List[ScheduleRead])
def list_schedules(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    return schedule_crud.list_for_user(db, current.id)


@router.post("", response_model=ScheduleRead, status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: ScheduleCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    return schedule_crud.create(db, user_id=current.id, payload=payload)


@router.patch("/{schedule_id}", response_model=ScheduleRead)
def update_schedule(
    schedule_id: uuid.UUID,
    payload: ScheduleUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    sched = schedule_crud.get_by_id(db, schedule_id)
    if not sched or sched.user_id != current.id:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule_crud.update(db, sched, **payload.model_dump(exclude_unset=True))


@router.delete("/{schedule_id}", status_code=204)
def delete_schedule(
    schedule_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    sched = schedule_crud.get_by_id(db, schedule_id)
    if not sched or sched.user_id != current.id:
        raise HTTPException(status_code=404, detail="Schedule not found")
    schedule_crud.delete(db, sched)