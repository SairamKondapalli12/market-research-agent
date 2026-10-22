"""FundingRound ORM model."""

import uuid
from typing import Optional

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class FundingRound(Base, TimestampMixin):
    __tablename__ = "funding_rounds"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("financial_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    round_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    amount: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    amount_usd_millions: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    round_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    lead_investor: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    investors: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    profile = relationship("FinancialProfile", back_populates="funding_rounds")

    def __repr__(self) -> str:
        return f"<FundingRound {self.round_name} {self.amount}>"