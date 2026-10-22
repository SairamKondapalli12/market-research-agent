"""Sentiment service — retrieval helpers."""

import uuid
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.database.crud import sentiment_crud


class SentimentService:

    @staticmethod
    def get_for_request(db: Session, request_id: uuid.UUID) -> List[Dict[str, Any]]:
        records = sentiment_crud.list_by_request(db, request_id)
        return [
            {
                "company": r.company,
                "score": r.score,
                "label": r.label,
                "distribution": r.distribution or {},
                "drivers": r.drivers or [],
                "summary": r.summary,
                "articles": r.articles or [],
            }
            for r in records
        ]