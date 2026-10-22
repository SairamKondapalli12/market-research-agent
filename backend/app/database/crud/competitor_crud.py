"""CRUD operations for Competitor."""

import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.database.models.competitor import Competitor


def create(
    db: Session,
    request_id: uuid.UUID,
    name: str,
    website: Optional[str] = None,
    description: Optional[str] = None,
    market_share_estimate: Optional[str] = None,
    headquarters: Optional[str] = None,
    founded_year: Optional[str] = None,
    is_direct: bool = True,
) -> Competitor:
    comp = Competitor(
        request_id=request_id,
        name=name,
        website=website,
        description=description,
        market_share_estimate=market_share_estimate,
        headquarters=headquarters,
        founded_year=founded_year,
        is_direct=is_direct,
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return comp


def bulk_create(db: Session, competitors: List[dict]) -> List[Competitor]:
    objs = [Competitor(**c) for c in competitors]
    db.add_all(objs)
    db.commit()
    for obj in objs:
        db.refresh(obj)
    return objs


def get_by_id(db: Session, competitor_id: uuid.UUID) -> Optional[Competitor]:
    return db.query(Competitor).filter(Competitor.id == competitor_id).first()


def list_by_request(db: Session, request_id: uuid.UUID) -> List[Competitor]:
    return (
        db.query(Competitor)
        .filter(Competitor.request_id == request_id)
        .order_by(Competitor.name.asc())
        .all()
    )


def delete(db: Session, competitor: Competitor) -> None:
    db.delete(competitor)
    db.commit()