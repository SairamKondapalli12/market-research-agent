"""Pydantic schemas for chat."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str
    content: str
    sources: Optional[list] = None
    created_at: datetime


class ChatAskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


class ChatAskResponse(BaseModel):
    conversation_id: uuid.UUID
    answer: str
    sources: List[dict] = []


class ChatConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    report_id: uuid.UUID
    title: Optional[str] = None
    created_at: datetime
    messages: List[ChatMessageRead] = []