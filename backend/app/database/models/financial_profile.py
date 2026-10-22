"""FinancialProfile ORM model."""

import uuid
from typing import Any, Optional

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class FinancialProfile(Base, TimestampMixin):
    __tablename__ = "financial_profiles"

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
    total_raised: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    total_raised_millions: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    latest_valuation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    estimated_revenue: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    investors: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    financial_signals: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    funding_rounds = relationship(
        "FundingRound", back_populates="profile", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<FinancialProfile company={self.company}>"