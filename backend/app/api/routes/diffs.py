"""Diff routes."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.crud import diff_crud, report_crud, research_crud
from app.database.models.user import User
from app.database.schemas.diff_schema import DiffRead
from app.database.session import get_db

router = APIRouter()


@router.get("/reports/{report_id}", response_model=DiffRead)
def get_diff_for_report(
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

    diff = diff_crud.get_by_current_report(db, report_id)
    if not diff:
        raise HTTPException(status_code=404, detail="No diff available for this report")
    return diff