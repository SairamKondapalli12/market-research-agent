"""Pydantic schemas for ResearchSchedule."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ScheduleCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=255)
    research_depth: str = Field("standard", pattern="^(quick|standard|deep)$")
    frequency: str = Field("weekly", pattern="^(daily|weekly|monthly)$")
    notes: Optional[str] = None


class ScheduleUpdate(BaseModel):
    frequency: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$")
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class ScheduleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_name: str
    industry: Optional[str]
    research_depth: str
    frequency: str
    is_active: bool
    last_run_at: Optional[str]
    next_run_at: Optional[str]
    runs_completed: int
    last_request_id: Optional[uuid.UUID]
    notes: Optional[str]
    created_at: datetime