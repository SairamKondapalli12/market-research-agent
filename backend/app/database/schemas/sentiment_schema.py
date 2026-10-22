"""Pydantic schemas for SentimentRecord."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class SentimentArticle(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    score: float
    label: str
    rationale: Optional[str] = None


class SentimentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_id: uuid.UUID
    company: str
    score: float
    label: str
    distribution: Optional[Dict[str, int]] = None
    drivers: Optional[List[str]] = None
    summary: Optional[str] = None
    articles: Optional[List[SentimentArticle]] = None
    created_at: datetime