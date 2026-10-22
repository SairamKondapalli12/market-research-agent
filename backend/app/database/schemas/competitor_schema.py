"""Pydantic schemas for Competitor."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CompetitorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_id: uuid.UUID
    name: str
    website: Optional[str] = None
    description: Optional[str] = None
    market_share_estimate: Optional[str] = None
    headquarters: Optional[str] = None
    founded_year: Optional[str] = None
    is_direct: Optional[bool] = True
    created_at: datetime