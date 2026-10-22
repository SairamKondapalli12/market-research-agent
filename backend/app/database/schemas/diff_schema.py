"""Pydantic schemas for ReportDiff."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class DiffRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    current_report_id: uuid.UUID
    previous_report_id: uuid.UUID
    request_id: uuid.UUID
    company_name: str
    significance: int
    summary: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    created_at: datetime


class DiffSummary(BaseModel):
    current_report_id: uuid.UUID
    previous_report_id: uuid.UUID
    company_name: str
    significance: int
    summary: str
    added_competitors: List[str] = []
    removed_competitors: List[str] = []
    new_events: List[Dict[str, Any]] = []
    new_recommendations: List[str] = []
    trend_changes: List[str] = []