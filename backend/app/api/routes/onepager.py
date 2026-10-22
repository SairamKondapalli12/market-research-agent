"""One-Pager route."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.crud import report_crud, research_crud
from app.database.models.user import User
from app.database.schemas.onepager_schema import OnePagerRead
from app.database.session import get_db
from app.services.onepager_service import OnePagerService

router = APIRouter()


@router.get("/reports/{report_id}", response_model=OnePagerRead)
def get_onepager(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    report = report_crud.get_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    parent = research_crud.get_by_id(db, report.request_id)
    if not parent or parent.user_id != current.id:
        raise HTTPException(status_code=404, detail="Report not found")

    result = OnePagerService.generate(report_id)
    return OnePagerRead(
        report_id=str(report_id),
        title=report.title,
        headline=result.get("headline", ""),
        key_points=result.get("key_points", []),
        action=result.get("action", ""),
    )