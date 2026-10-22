"""Watchlist routes."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.models.user import User
from app.database.models.watchlist import Watchlist
from app.database.session import get_db


router = APIRouter()


class WatchlistCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    monitoring_frequency: str = Field("weekly", pattern="^(daily|weekly|monthly)$")
    notes: str | None = None


class WatchlistUpdate(BaseModel):
    monitoring_frequency: str | None = Field(None, pattern="^(daily|weekly|monthly)$")
    is_active: bool | None = None
    notes: str | None = None


class WatchlistRead(BaseModel):
    id: uuid.UUID
    company_name: str
    monitoring_frequency: str
    is_active: bool
    last_checked: str | None
    notes: str | None

    class Config:
        from_attributes = True


@router.get("", response_model=List[WatchlistRead])
def list_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Watchlist)
        .filter(Watchlist.user_id == current_user.id)
        .order_by(Watchlist.created_at.desc())
        .all()
    )


@router.post("", response_model=WatchlistRead, status_code=status.HTTP_201_CREATED)
def add_to_watchlist(
    payload: WatchlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = (
        db.query(Watchlist)
        .filter(
            Watchlist.user_id == current_user.id,
            Watchlist.company_name == payload.company_name,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Company already in watchlist")

    item = Watchlist(
        user_id=current_user.id,
        company_name=payload.company_name,
        monitoring_frequency=payload.monitoring_frequency,
        notes=payload.notes,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=WatchlistRead)
def update_watchlist_item(
    item_id: uuid.UUID,
    payload: WatchlistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(Watchlist)
        .filter(Watchlist.id == item_id, Watchlist.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")

    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_watchlist_item(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = (
        db.query(Watchlist)
        .filter(Watchlist.id == item_id, Watchlist.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    db.delete(item)
    db.commit()