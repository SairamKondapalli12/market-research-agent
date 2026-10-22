"""Chat with Report routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.config.logging_config import get_logger
from app.config.settings import settings
from app.database.crud import chat_crud, report_crud, research_crud
from app.database.models.user import User
from app.database.schemas.chat_schema import (
    ChatAskRequest,
    ChatAskResponse,
    ChatConversationRead,
)
from app.database.session import get_db
from app.services.rag_service import RAGService

router = APIRouter()
logger = get_logger(__name__)


def _build_llm():
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.startswith("your-"):
        return None
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3,
            max_output_tokens=8192,
            timeout=60,
            convert_system_message_to_human=True,
        )
    except Exception as exc:
        logger.error(f"Chat LLM init failed: {exc}")
        return None


def _assert_report_access(db: Session, report_id: uuid.UUID, user_id: uuid.UUID):
    report = report_crud.get_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    parent = research_crud.get_by_id(db, report.request_id)
    if not parent or parent.user_id != user_id:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/reports/{report_id}", response_model=ChatConversationRead)
def get_conversation(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _assert_report_access(db, report_id, current_user.id)
    conv = chat_crud.get_or_create_conversation(db, current_user.id, report_id)
    return conv


@router.post("/reports/{report_id}/ask", response_model=ChatAskResponse)
def ask(
    report_id: uuid.UUID,
    payload: ChatAskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _assert_report_access(db, report_id, current_user.id)

    conv = chat_crud.get_or_create_conversation(db, current_user.id, report_id)
    chat_crud.add_message(db, conv.id, "user", payload.question)

    service = RAGService(llm=_build_llm())
    result = service.ask(db, report_id, payload.question)

    chat_crud.add_message(
        db, conv.id, "assistant", result["answer"], sources=result["sources"]
    )

    return ChatAskResponse(
        conversation_id=conv.id,
        answer=result["answer"],
        sources=result["sources"],
    )