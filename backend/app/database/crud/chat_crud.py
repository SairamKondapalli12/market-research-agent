"""CRUD for ChatConversation and ChatMessage."""

import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.database.models.chat_conversation import ChatConversation
from app.database.models.chat_message import ChatMessage


def get_or_create_conversation(
    db: Session, user_id: uuid.UUID, report_id: uuid.UUID
) -> ChatConversation:
    existing = (
        db.query(ChatConversation)
        .filter(
            ChatConversation.user_id == user_id,
            ChatConversation.report_id == report_id,
        )
        .first()
    )
    if existing:
        return existing
    conv = ChatConversation(user_id=user_id, report_id=report_id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def list_messages(db: Session, conversation_id: uuid.UUID) -> List[ChatMessage]:
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


def add_message(
    db: Session,
    conversation_id: uuid.UUID,
    role: str,
    content: str,
    sources: Optional[list] = None,
) -> ChatMessage:
    msg = ChatMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
        sources=sources,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_conversation(db: Session, conversation_id: uuid.UUID) -> Optional[ChatConversation]:
    return (
        db.query(ChatConversation)
        .filter(ChatConversation.id == conversation_id)
        .first()
    )