"""Pydantic schemas for IntelligenceEvent."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class IntelligenceEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_id: uuid.UUID
    company: str
    event_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    significance: int
    source_url: Optional[str] = None
    event_date: Optional[str] = None
    created_at: datetime