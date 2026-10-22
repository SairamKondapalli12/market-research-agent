"""Research request routes."""

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.crud import research_crud
from app.database.models.user import User
from app.database.schemas.research_schema import (
    ResearchRequestCreate,
    ResearchRequestDetail,
    ResearchRequestRead,
)
from app.database.session import get_db
from app.services.activity_service import record as record_activity
from app.services.research_service import ResearchService


router = APIRouter()


@router.post("", response_model=ResearchRequestRead, status_code=status.HTTP_201_CREATED)
def create_research(
    payload: ResearchRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = research_crud.create(db, user_id=current_user.id, data=payload)

    record_activity(
        action="research.started",
        actor=current_user.email,
        user_id=current_user.id,
        target_type="research",
        target_id=str(req.id),
        target_label=payload.company_name,
        level="info",
    )

    service = ResearchService()
    background_tasks.add_task(
        service.run_pipeline,
        request_id=str(req.id),
        user_id=str(current_user.id),
    )
    return req


@router.get("", response_model=list[ResearchRequestRead])
def list_research(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return research_crud.list_by_user(db, current_user.id, skip=skip, limit=limit)


@router.get("/{request_id}", response_model=ResearchRequestDetail)
def get_research(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = research_crud.get_by_id(db, request_id)
    if not req or req.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Research request not found")

    detail = ResearchRequestDetail.model_validate(req)
    detail.competitors = list(req.competitors)
    detail.intelligence_events = list(req.intelligence_events)
    detail.reports = list(req.reports)
    return detail


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_research(
    request_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = research_crud.get_by_id(db, request_id)
    if not req or req.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Research request not found")
    research_crud.delete(db, req)
    record_activity(
        action="research.deleted",
        actor=current_user.email,
        user_id=current_user.id,
        target_type="research",
        target_id=str(request_id),
        target_label=req.company_name,
        level="warning",
    )


@router.post("/{request_id}/retry", response_model=ResearchRequestRead)
def retry_research(
    request_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    req = research_crud.get_by_id(db, request_id)
    if not req or req.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Research request not found")

    research_crud.update_status(db, request_id, "pending", 0, None)
    service = ResearchService()
    background_tasks.add_task(
        service.run_pipeline,
        request_id=str(req.id),
        user_id=str(current_user.id),
    )
    return req