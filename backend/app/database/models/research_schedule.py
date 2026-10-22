"""ResearchSchedule ORM model."""

import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base, TimestampMixin


class ResearchSchedule(Base, TimestampMixin):
    __tablename__ = "research_schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    research_depth: Mapped[str] = mapped_column(String(50), default="standard", nullable=False)
    frequency: Mapped[str] = mapped_column(String(50), default="weekly", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_run_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    next_run_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    runs_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_request_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<ResearchSchedule {self.company_name} {self.frequency}>"