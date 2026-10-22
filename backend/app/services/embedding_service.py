"""Embedding service — creates vector embeddings for text."""

from typing import List, Optional

from app.config.logging_config import get_logger
from app.config.settings import settings

logger = get_logger(__name__)


class EmbeddingService:

    @staticmethod
    def embed(text: str) -> Optional[List[float]]:
        """Return a vector embedding for the text, or None if unavailable."""
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.startswith("your-"):
            return None
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            result = genai.embed_content(
                model="models/gemini-embedding-001",
                content=text[:8000],
            )
            embedding = list(result.get("embedding") or [])
            if not embedding:
                return None
            # Normalise to configured dimension
            target = settings.EMBEDDING_DIMENSION
            if len(embedding) < target:
                embedding += [0.0] * (target - len(embedding))
            elif len(embedding) > target:
                embedding = embedding[:target]
            return embedding
        except Exception as exc:
            logger.warning(f"Embedding failed: {exc}")
            return None


embedding_service = EmbeddingService()
