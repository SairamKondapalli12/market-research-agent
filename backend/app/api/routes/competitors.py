"""Competitor routes."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.crud import competitor_crud, research_crud
from app.database.models.user import User
from app.database.schemas.competitor_schema import CompetitorRead
from app.database.session import get_db


router = APIRouter()


@router.get("", response_model=List[CompetitorRead])
def list_competitors(
    request_id: uuid.UUID = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if request_id:
        req = research_crud.get_by_id(db, request_id)
        if not req or req.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Research request not found")
        return competitor_crud.list_by_request(db, request_id)

    # Otherwise, aggregate all competitors across the user's requests
    all_competitors = []
    reqs = research_crud.list_by_user(db, current_user.id, skip=0, limit=1000)
    for req in reqs:
        all_competitors.extend(req.competitors)
    return all_competitors


@router.get("/{competitor_id}", response_model=CompetitorRead)
def get_competitor(
    competitor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comp = competitor_crud.get_by_id(db, competitor_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")

    parent = research_crud.get_by_id(db, comp.request_id)
    if not parent or parent.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Competitor not found")
    return comp


@router.delete("/{competitor_id}", status_code=204)
def delete_competitor(
    competitor_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comp = competitor_crud.get_by_id(db, competitor_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Competitor not found")

    parent = research_crud.get_by_id(db, comp.request_id)
    if not parent or parent.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Competitor not found")
    competitor_crud.delete(db, comp)