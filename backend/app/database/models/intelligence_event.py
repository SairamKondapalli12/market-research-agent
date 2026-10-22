"""IntelligenceEvent ORM model — extracted competitive intelligence."""

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class IntelligenceEvent(Base, TimestampMixin):
    __tablename__ = "intelligence_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    company: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    significance: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    research_request = relationship(
        "ResearchRequest", back_populates="intelligence_events"
    )

    def __repr__(self) -> str:
        return f"<IntelligenceEvent company={self.company} type={self.event_type} score={self.significance}>"