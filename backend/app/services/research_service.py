"""Research orchestration service."""

from typing import Any, Dict

from app.agents.manager_agent import ManagerAgent
from app.config.logging_config import get_logger
from app.database.crud import research_crud
from app.database.session import SessionLocal

logger = get_logger(__name__)


class ResearchService:
    def __init__(self):
        self.llm = self._build_llm()

    @staticmethod
    def _build_llm():
        from app.config.settings import settings
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.startswith("your-"):
            logger.warning("GEMINI_API_KEY not set — LLM calls skipped.")
            return None
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=settings.GEMINI_TEMPERATURE,
                max_output_tokens=8192,
                timeout=60,
                convert_system_message_to_human=True,
            )
        except Exception as exc:
            logger.error(f"Gemini init failed: {exc}")
            return None

    def run_pipeline(self, request_id: str, user_id: str) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            req = research_crud.get_by_id(db, request_id)
            if not req:
                return {"success": False, "error": "Request not found"}
            known = req.known_competitors.split(",") if req.known_competitors else []
            inputs = {
                "request_id": str(req.id),
                "company_name": req.company_name,
                "industry": req.industry,
                "known_competitors": known,
                "research_depth": req.research_depth,
                "user_id": user_id,
            }
        finally:
            db.close()

        manager = ManagerAgent(llm=self.llm, verbose=False, request_id=request_id)
        return manager.run(inputs)