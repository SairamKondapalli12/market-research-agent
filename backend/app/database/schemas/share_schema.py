"""Pydantic schemas for ShareLink."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ShareLinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    token: str
    report_id: uuid.UUID
    views: int
    created_at: datetime
    expires_at: Optional[str] = None


class SharedReportRead(BaseModel):
    """Public-facing report payload (no private fields)."""

    id: uuid.UUID
    title: str
    executive_summary: Optional[str] = None
    report_content: Optional[str] = None
    swot_analysis: Optional[dict] = None
    trends: Optional[dict] = None
    recommendations: Optional[dict] = None
    confidence_score: Optional[int] = None
    created_at: datetime