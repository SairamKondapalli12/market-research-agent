"""Intelligence feed routes — unified event feed."""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.models.intelligence_event import IntelligenceEvent
from app.database.models.research_request import ResearchRequest
from app.database.models.user import User
from app.database.schemas.event_schema import IntelligenceEventRead
from app.database.session import get_db


router = APIRouter()


@router.get("", response_model=List[IntelligenceEventRead])
def get_feed(
    event_type: Optional[str] = None,
    company: Optional[str] = None,
    min_significance: int = Query(1, ge=1, le=10),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only events belonging to the user's research requests
    query = (
        db.query(IntelligenceEvent)
        .join(ResearchRequest, IntelligenceEvent.request_id == ResearchRequest.id)
        .filter(ResearchRequest.user_id == current_user.id)
    )
    if event_type:
        query = query.filter(IntelligenceEvent.event_type == event_type)
    if company:
        query = query.filter(IntelligenceEvent.company.ilike(f"%{company}%"))
    query = query.filter(IntelligenceEvent.significance >= min_significance)

    return (
        query.order_by(
            IntelligenceEvent.significance.desc(),
            IntelligenceEvent.created_at.desc(),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )