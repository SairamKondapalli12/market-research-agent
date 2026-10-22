"""Report routes."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.crud import report_crud, research_crud
from app.database.models.user import User
from app.database.schemas.report_schema import ReportRead, ReportSummary
from app.database.session import get_db


router = APIRouter()


@router.get("", response_model=List[ReportSummary])
def list_reports(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reqs = research_crud.list_by_user(db, current_user.id, skip=0, limit=1000)
    summaries = []
    for req in reqs:
        for r in req.reports:
            summaries.append(ReportSummary.model_validate(r))
    return summaries[skip : skip + limit]


@router.get("/{report_id}", response_model=ReportRead)
def get_report(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = report_crud.get_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    parent = research_crud.get_by_id(db, report.request_id)
    if not parent or parent.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/{report_id}/export/markdown", response_class=PlainTextResponse)
def export_markdown(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = report_crud.get_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    parent = research_crud.get_by_id(db, report.request_id)
    if not parent or parent.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Report not found")
    headers = {"Content-Disposition": f'attachment; filename="report-{report_id}.md"'}
    return PlainTextResponse(report.report_content or "", headers=headers)