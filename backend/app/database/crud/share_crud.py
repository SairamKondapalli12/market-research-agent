"""CRUD for ShareLink."""

import secrets
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.database.models.share_link import ShareLink


def create(db: Session, report_id: uuid.UUID, user_id: uuid.UUID) -> ShareLink:
    token = secrets.token_urlsafe(24)
    link = ShareLink(token=token, report_id=report_id, user_id=user_id)
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


def get_by_token(db: Session, token: str) -> Optional[ShareLink]:
    return db.query(ShareLink).filter(ShareLink.token == token).first()


def get_or_create(db: Session, report_id: uuid.UUID, user_id: uuid.UUID) -> ShareLink:
    existing = (
        db.query(ShareLink)
        .filter(ShareLink.report_id == report_id, ShareLink.user_id == user_id)
        .first()
    )
    if existing:
        return existing
    return create(db, report_id=report_id, user_id=user_id)


def increment_views(db: Session, link: ShareLink) -> None:
    link.views += 1
    db.commit()