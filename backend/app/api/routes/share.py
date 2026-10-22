"""Share link routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.crud import report_crud, research_crud, share_crud
from app.database.models.user import User
from app.database.schemas.share_schema import ShareLinkRead, SharedReportRead
from app.database.session import get_db

router = APIRouter()


@router.post("/reports/{report_id}", response_model=ShareLinkRead)
def create_or_get_share(
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
    return share_crud.get_or_create(db, report_id, current.id)


@router.get("/public/{token}", response_model=SharedReportRead)
def read_shared(token: str, db: Session = Depends(get_db)):
    link = share_crud.get_by_token(db, token)
    if not link:
        raise HTTPException(status_code=404, detail="Share link not found")
    report = report_crud.get_by_id(db, link.report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report no longer exists")
    share_crud.increment_views(db, link)
    return SharedReportRead.model_validate(report)