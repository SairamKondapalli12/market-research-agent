"""Report ORM model — generated research output."""

import uuid
from typing import Any, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("research_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    executive_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    report_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    swot_analysis: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    trends: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    recommendations: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    confidence_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ─── Feature expansion ─────────────────────────────────────
    previous_report_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reports.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sentiment_summary: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    financial_summary: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    onepager: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    diff_significance: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    research_request = relationship("ResearchRequest", back_populates="reports")

    def __repr__(self) -> str:
        return f"<Report id={self.id} title={self.title[:60]}>"