"""User ORM model."""

import uuid
from typing import Optional

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Per-user API keys (encrypted at rest in production)
    gemini_api_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tavily_api_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Notification preferences
    email_notifications: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # Relationships
    research_requests = relationship(
        "ResearchRequest", back_populates="user", cascade="all, delete-orphan"
    )
    watchlist_items = relationship(
        "Watchlist", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"