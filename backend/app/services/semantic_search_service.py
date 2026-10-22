"""Semantic search service using pgvector."""

from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.logging_config import get_logger
from app.config.settings import settings


logger = get_logger(__name__)


class SemanticSearchService:
    """Performs vector similarity search over stored articles."""

    @staticmethod
    def embed_text(text_content: str) -> Optional[List[float]]:
        """
        Return an embedding for the given text.

        Uses Gemini's embedding endpoint if configured; otherwise returns None
        and callers should fall back to lexical search.
        """
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.startswith("your-"):
            return None
        try:
            import google.generativeai as genai

            genai.configure(api_key=settings.GEMINI_API_KEY)
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text_content[:8000],
            )
            embedding = result.get("embedding")
            if embedding and len(embedding) != settings.EMBEDDING_DIMENSION:
                # Pad or truncate to match the configured dimension
                if len(embedding) < settings.EMBEDDING_DIMENSION:
                    embedding = list(embedding) + [0.0] * (
                        settings.EMBEDDING_DIMENSION - len(embedding)
                    )
                else:
                    embedding = list(embedding[: settings.EMBEDDING_DIMENSION])
            return embedding
        except Exception as exc:
            logger.warning(f"Embedding failed: {exc}")
            return None

    @staticmethod
    def search_articles(
        db: Session,
        query: str,
        limit: int = 10,
        request_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        embedding = SemanticSearchService.embed_text(query)
        if embedding is None:
            # Fallback: full-text search on title/content
            sql = """
                SELECT id, url, title, content, source
                FROM articles
                WHERE (title ILIKE :q OR content ILIKE :q)
                {req_filter}
                ORDER BY created_at DESC
                LIMIT :limit
            """.format(req_filter="AND request_id = :req_id" if request_id else "")
            params: Dict[str, Any] = {
                "q": f"%{query}%",
                "limit": limit,
            }
            if request_id:
                params["req_id"] = request_id
            rows = db.execute(text(sql), params).mappings().all()
            return [dict(r) for r in rows]

        # Vector similarity search
        sql = """
            SELECT id, url, title, content, source,
                   1 - (embedding <=> :embedding) AS similarity
            FROM articles
            WHERE embedding IS NOT NULL
            {req_filter}
            ORDER BY embedding <=> :embedding
            LIMIT :limit
        """.format(req_filter="AND request_id = :req_id" if request_id else "")
        params = {
            "embedding": embedding,
            "limit": limit,
        }
        if request_id:
            params["req_id"] = request_id

        rows = db.execute(text(sql), params).mappings().all()
        return [dict(r) for r in rows]