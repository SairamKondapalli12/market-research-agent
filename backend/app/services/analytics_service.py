"""Aggregation queries for the analytics dashboard."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.models.research_request import ResearchRequest
from app.database.models.report import Report
from app.database.models.competitor import Competitor
from app.database.models.intelligence_event import IntelligenceEvent


def research_over_time(db: Session, user_id, days: int = 14) -> List[Dict[str, Any]]:
    """Return research request count grouped by day."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(
            func.date(ResearchRequest.created_at).label("date"),
            func.count(ResearchRequest.id).label("count"),
        )
        .filter(
            ResearchRequest.user_id == user_id,
            ResearchRequest.created_at >= since,
        )
        .group_by(func.date(ResearchRequest.created_at))
        .order_by(func.date(ResearchRequest.created_at))
        .all()
    )
    return [{"date": str(r.date), "count": r.count} for r in rows]


def summary(db: Session, user_id) -> Dict[str, Any]:
    """Aggregate summary stats."""
    total_research = (
        db.query(func.count(ResearchRequest.id))
        .filter(ResearchRequest.user_id == user_id)
        .scalar()
        or 0
    )
    total_reports = (
        db.query(func.count(Report.id))
        .join(ResearchRequest, Report.request_id == ResearchRequest.id)
        .filter(ResearchRequest.user_id == user_id)
        .scalar()
        or 0
    )
    total_competitors = (
        db.query(func.count(Competitor.id))
        .join(ResearchRequest, Competitor.request_id == ResearchRequest.id)
        .filter(ResearchRequest.user_id == user_id)
        .scalar()
        or 0
    )
    total_events = (
        db.query(func.count(IntelligenceEvent.id))
        .join(ResearchRequest, IntelligenceEvent.request_id == ResearchRequest.id)
        .filter(ResearchRequest.user_id == user_id)
        .scalar()
        or 0
    )
    avg_confidence = (
        db.query(func.avg(Report.confidence_score))
        .join(ResearchRequest, Report.request_id == ResearchRequest.id)
        .filter(ResearchRequest.user_id == user_id)
        .scalar()
    )
    return {
        "total_research": total_research,
        "total_reports": total_reports,
        "total_competitors": total_competitors,
        "total_events": total_events,
        "avg_confidence": round(avg_confidence or 0),
    }


def system_health(db: Session) -> Dict[str, Any]:
    """System-wide metrics for admin console."""
    from app.database.models.user import User
    from app.database.models.intelligence_event import IntelligenceEvent

    total_users = db.query(func.count(User.id)).scalar() or 0
    active_users = (
        db.query(func.count(User.id)).filter(User.is_active.is_(True)).scalar() or 0
    )
    total_reports = db.query(func.count(Report.id)).scalar() or 0
    total_research = db.query(func.count(ResearchRequest.id)).scalar() or 0
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_reports": total_reports,
        "total_research": total_research,
    }