"""Report comparison route."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.crud import report_crud, research_crud
from app.database.models.user import User
from app.database.schemas.compare_schema import ReportCompare
from app.database.session import get_db
from app.services.compare_service import CompareService

router = APIRouter()


@router.get("", response_model=ReportCompare)
def compare_reports(
    left: uuid.UUID = Query(...),
    right: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    # Verify ownership on both
    for rid in (left, right):
        r = report_crud.get_by_id(db, rid)
        if not r:
            raise HTTPException(status_code=404, detail="Report not found")
        parent = research_crud.get_by_id(db, r.request_id)
        if not parent or parent.user_id != current.id:
            raise HTTPException(status_code=404, detail="Report not found")

    try:
        result = CompareService.compare(db, left, right)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return result