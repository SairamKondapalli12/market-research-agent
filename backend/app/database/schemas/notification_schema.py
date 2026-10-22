"""Pydantic schemas for Notification."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str
    title: str
    body: Optional[str] = None
    link: Optional[str] = None
    is_read: bool
    created_at: datetime


class NotificationCreate(BaseModel):
    user_id: uuid.UUID
    type: str
    title: str
    body: Optional[str] = None
    link: Optional[str] = None