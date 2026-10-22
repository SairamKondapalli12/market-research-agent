"""Pydantic schemas for Report."""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class ReportSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    confidence_score: Optional[int] = None
    diff_significance: Optional[int] = None
    created_at: datetime


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_id: uuid.UUID
    title: str
    executive_summary: Optional[str] = None
    report_content: Optional[str] = None
    swot_analysis: Optional[Dict[str, Any]] = None
    trends: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    confidence_score: Optional[int] = None
    previous_report_id: Optional[uuid.UUID] = None
    sentiment_summary: Optional[Dict[str, Any]] = None
    financial_summary: Optional[Dict[str, Any]] = None
    onepager: Optional[Dict[str, Any]] = None
    diff_significance: Optional[int] = None
    created_at: datetime
    updated_at: datetime