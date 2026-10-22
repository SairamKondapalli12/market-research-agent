"""CRUD operations for Article."""

import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.database.models.article import Article


def create(
    db: Session,
    request_id: uuid.UUID,
    url: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    source: Optional[str] = None,
    author: Optional[str] = None,
    published_date: Optional[str] = None,
    embedding: Optional[list] = None,
) -> Article:
    article = Article(
        request_id=request_id,
        url=url,
        title=title,
        content=content,
        source=source,
        author=author,
        published_date=published_date,
        embedding=embedding,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def bulk_create(db: Session, articles: List[dict]) -> List[Article]:
    objs = [Article(**a) for a in articles]
    db.add_all(objs)
    db.commit()
    for obj in objs:
        db.refresh(obj)
    return objs


def get_by_id(db: Session, article_id: uuid.UUID) -> Optional[Article]:
    return db.query(Article).filter(Article.id == article_id).first()


def list_by_request(db: Session, request_id: uuid.UUID) -> List[Article]:
    return (
        db.query(Article)
        .filter(Article.request_id == request_id)
        .order_by(Article.created_at.desc())
        .all()
    )


def exists_by_url(db: Session, request_id: uuid.UUID, url: str) -> bool:
    return (
        db.query(Article.id)
        .filter(Article.request_id == request_id, Article.url == url)
        .first()
        is not None
    )