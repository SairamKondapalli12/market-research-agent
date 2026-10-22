"""Pydantic schemas for ResearchRequest."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.database.schemas.competitor_schema import CompetitorRead
from app.database.schemas.event_schema import IntelligenceEventRead
from app.database.schemas.report_schema import ReportSummary


class ResearchRequestCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=255)
    known_competitors: Optional[List[str]] = None
    research_depth: str = Field("standard", pattern="^(quick|standard|deep)$")


class ResearchRequestUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    error_message: Optional[str] = None


class ResearchRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    company_name: str
    industry: Optional[str]
    research_depth: str
    status: str
    progress: int
    sources_count: int
    events_count: int
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime


class ResearchRequestDetail(ResearchRequestRead):
    competitors: List[CompetitorRead] = []
    intelligence_events: List[IntelligenceEventRead] = []
    reports: List[ReportSummary] = []