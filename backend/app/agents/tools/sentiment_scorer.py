"""Rule-based sentiment fallback scorer."""

from typing import Dict

POSITIVE_TERMS = {
    "growth", "breakthrough", "leader", "surge", "record", "innovative",
    "partnership", "acquisition", "expand", "milestone", "award", "launch",
    "raise", "profit", "success", "adoption", "trusted", "excellent",
    "advance", "strong", "impressive", "best", "top", "winner",
}

NEGATIVE_TERMS = {
    "lawsuit", "layoff", "decline", "loss", "controversy", "scandal",
    "shutdown", "breach", "hack", "fail", "failure", "concern", "criticism",
    "delay", "recall", "investigation", "fine", "penalty", "struggle",
    "drop", "cut", "slump", "weak", "worse", "worst",
}


class SentimentScorerTool:
    """Fast, deterministic fallback scorer (used when LLM is unavailable)."""

    def score(self, text: str) -> Dict[str, object]:
        if not text:
            return {"score": 0.0, "label": "neutral", "rationale": "Empty input."}

        lower = text.lower()
        pos = sum(1 for t in POSITIVE_TERMS if t in lower)
        neg = sum(1 for t in NEGATIVE_TERMS if t in lower)

        total = pos + neg
        if total == 0:
            return {"score": 0.0, "label": "neutral", "rationale": "No strong signals detected."}

        raw = (pos - neg) / total
        score = max(-1.0, min(1.0, raw))

        if score > 0.15:
            label = "positive"
        elif score < -0.15:
            label = "negative"
        else:
            label = "neutral"

        rationale = (
            f"Detected {pos} positive and {neg} negative signals."
        )
        return {"score": round(score, 3), "label": label, "rationale": rationale}