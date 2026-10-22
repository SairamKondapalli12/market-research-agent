"""SentimentRecord ORM model."""

import uuid
from typing import Any, Optional

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class SentimentRecord(Base, TimestampMixin):
    __tablename__ = "sentiment_records"

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
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    label: Mapped[str] = mapped_column(String(20), default="neutral", nullable=False)
    distribution: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    drivers: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    articles: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)

    research_request = relationship("ResearchRequest", backref="sentiment_records")

    def __repr__(self) -> str:
        return f"<SentimentRecord company={self.company} score={self.score}>"