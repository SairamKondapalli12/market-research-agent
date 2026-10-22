"""ResearchRequest ORM model."""

import uuid
from typing import List, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class ResearchRequest(Base, TimestampMixin):
    __tablename__ = "research_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    industry: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    known_competitors: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    research_depth: Mapped[str] = mapped_column(String(50), default="standard", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False, index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sources_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    events_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    completed_at: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    user = relationship("User", back_populates="research_requests")
    articles = relationship(
        "Article", back_populates="research_request", cascade="all, delete-orphan"
    )
    intelligence_events = relationship(
        "IntelligenceEvent", back_populates="research_request", cascade="all, delete-orphan"
    )
    reports = relationship(
        "Report", back_populates="research_request", cascade="all, delete-orphan"
    )
    competitors = relationship(
        "Competitor", back_populates="research_request", cascade="all, delete-orphan"
    )
    agent_events = relationship(
        "AgentLogEvent", cascade="all, delete-orphan", order_by="AgentLogEvent.sequence"
    )

    def __repr__(self) -> str:
        return f"<ResearchRequest id={self.id} company={self.company_name} status={self.status}>"