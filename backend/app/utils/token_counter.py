"""Rough token counting for LLM prompt budgeting."""

from typing import Optional


class TokenCounter:
    """Estimate token counts without a full tokenizer dependency."""

    @staticmethod
    def estimate(text: str) -> int:
        if not text:
            return 0
        try:
            import tiktoken

            enc = tiktoken.get_encoding("cl100k_base")
            return len(enc.encode(text))
        except Exception:
            # Fallback heuristic: ~4 chars per token for English
            return max(1, len(text) // 4)

    @staticmethod
    def fits(text: str, max_tokens: int, reserve_for_output: int = 0) -> bool:
        return TokenCounter.estimate(text) + reserve_for_output <= max_tokens

    @staticmethod
    def truncate_to_tokens(text: str, max_tokens: int) -> str:
        if not text:
            return ""
        if TokenCounter.estimate(text) <= max_tokens:
            return text
        try:
            import tiktoken

            enc = tiktoken.get_encoding("cl100k_base")
            tokens = enc.encode(text)[:max_tokens]
            return enc.decode(tokens)
        except Exception:
            return text[: max_tokens * 4]