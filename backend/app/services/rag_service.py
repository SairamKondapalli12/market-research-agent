"""RAG service — answers user questions using only stored report sources."""

import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.logging_config import get_logger
from app.config.settings import settings
from app.database.crud import article_crud, report_crud
from app.services.embedding_service import embedding_service

logger = get_logger(__name__)


class RAGService:
    """Retrieval-Augmented Generation over a single report's source set."""

    MAX_CONTEXT_ARTICLES = 8
    MAX_CONTEXT_TOKENS = 6000
    MAX_ANSWER_TOKENS = 600

    def __init__(self, llm=None):
        self.llm = llm

    # ─── Helpers ────────────────────────────────────────────
    @staticmethod
    def _to_pgvector_literal(embedding: List[float]) -> str:
        """Serialize a Python list to the pgvector literal format: '[0.1,0.2,...]'."""
        return "[" + ",".join(f"{x:.6f}" for x in embedding) + "]"

    # ─── Retrieval ──────────────────────────────────────────
    def _retrieve(
        self, db: Session, request_id: uuid.UUID, question: str
    ) -> List[Dict[str, Any]]:
        """
        Return top-K articles for the given question.
        Never leaves the session in an aborted state.
        """
        embedding = embedding_service.embed(question)

        if embedding is not None:
            embedding_literal = self._to_pgvector_literal(embedding)

            sql = text(
                """
                SELECT id, url, title, content, source,
                       1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
                FROM articles
                WHERE request_id = :req_id AND embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :limit
                """
            )
            try:
                rows = db.execute(
                    sql,
                    {
                        "embedding": embedding_literal,
                        "req_id": str(request_id),
                        "limit": self.MAX_CONTEXT_ARTICLES,
                    },
                ).mappings().all()
                if rows:
                    return [dict(r) for r in rows]
            except Exception as exc:
                logger.warning(f"Vector search failed, rolling back: {exc}")
                db.rollback()

        # Fallback: full-text search
        sql = text(
            """
            SELECT id, url, title, content, source
            FROM articles
            WHERE request_id = :req_id
              AND (title ILIKE :q OR content ILIKE :q)
            ORDER BY created_at DESC
            LIMIT :limit
            """
        )
        try:
            rows = db.execute(
                sql,
                {
                    "req_id": str(request_id),
                    "q": f"%{question[:80]}%",
                    "limit": self.MAX_CONTEXT_ARTICLES,
                },
            ).mappings().all()
            if rows:
                return [dict(r) for r in rows]
        except Exception as exc:
            logger.warning(f"Full-text search failed, rolling back: {exc}")
            db.rollback()

        # Last resort: latest N articles
        try:
            arts = article_crud.list_by_request(db, request_id)[: self.MAX_CONTEXT_ARTICLES]
            return [
                {
                    "id": str(a.id),
                    "url": a.url,
                    "title": a.title,
                    "content": a.content,
                    "source": a.source,
                }
                for a in arts
            ]
        except Exception as exc:
            logger.warning(f"Fallback query failed: {exc}")
            db.rollback()
            return []

    # ─── Generation ─────────────────────────────────────────
    def _build_prompt(
        self,
        question: str,
        report: Any,
        articles: List[Dict[str, Any]],
    ) -> str:
        context_parts = []
        for i, a in enumerate(articles, start=1):
            snippet = (a.get("content") or "")[:1200]
            context_parts.append(
                f"[Source {i}] {a.get('title') or 'Untitled'}\n"
                f"URL: {a.get('url') or 'n/a'}\n"
                f"Excerpt:\n{snippet}\n"
            )
        context = "\n---\n".join(context_parts)

        return f"""You are answering questions about a market research report.

Report title: {getattr(report, 'title', 'N/A')}

Executive summary:
{getattr(report, 'executive_summary', '') or '(none)'}

Full report content (Markdown):
{(getattr(report, 'report_content', '') or '')[:4000]}

Source excerpts from the underlying research:
{context}

User question: {question}

Instructions:
- Answer only using the report content and source excerpts above.
- If the answer is not supported by the sources, say so plainly.
- Be concise (under 200 words unless asked to expand).
- Cite sources by number when relevant (e.g. "[Source 3]").
"""

    def _generate(self, prompt: str) -> str:
        if self.llm is None:
            return (
                "The chat feature requires an LLM connection. "
                "Please ensure GEMINI_API_KEY is configured."
            )
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as exc:
            logger.error(f"RAG generation failed: {exc}")
            return "I encountered an error while generating the answer. Please try again."

    # ─── Public API ─────────────────────────────────────────
    def ask(
        self, db: Session, report_id: uuid.UUID, question: str
    ) -> Dict[str, Any]:
        report = report_crud.get_by_id(db, report_id)
        if not report:
            raise ValueError("Report not found")

        articles = self._retrieve(db, report.request_id, question)
        prompt = self._build_prompt(question, report, articles)
        answer = self._generate(prompt)

        sources = [
            {"title": a.get("title"), "url": a.get("url"), "source": a.get("source")}
            for a in articles[:5]
        ]
        return {"answer": answer, "sources": sources}