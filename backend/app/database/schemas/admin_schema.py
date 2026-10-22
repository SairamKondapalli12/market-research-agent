"""Pydantic schemas for the admin console."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AdminUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: Optional[str] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime


class SystemHealth(BaseModel):
    database: str
    redis: str
    pipeline: str
    api: str
    storage_used: str
    storage_total: str
    storage_percent: int
    total_users: int
    active_users: int
    total_reports: int
    total_research: int


class AdminOverview(BaseModel):
    total_users: int
    active_sessions: int
    queue_depth: int
    api_latency_ms: int