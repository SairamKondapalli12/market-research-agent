"""Significance scorer — assign 1-10 impact score to events."""

from app.config.constants import EventType


class SignificanceScorerTool:
    """
    Deterministic scorer that combines a base score per event type with
    modifiers for monetary amounts, leadership changes, and legal language.
    """

    BASE_SCORES = {
        EventType.ACQUISITION.value: 8,
        EventType.FUNDING.value: 7,
        EventType.LEADERSHIP_CHANGE.value: 6,
        EventType.PRODUCT_LAUNCH.value: 6,
        EventType.PARTNERSHIP.value: 5,
        EventType.PRICING_CHANGE.value: 5,
        EventType.EXPANSION.value: 5,
        EventType.HIRING.value: 4,
        EventType.LAYOFF.value: 5,
        EventType.LEGAL.value: 6,
        EventType.MARKET_TREND.value: 4,
        EventType.OTHER.value: 3,
    }

    HIGH_IMPACT_KEYWORDS = {
        "billion": 2,
        "acquisition": 1,
        "merger": 1,
        "ceo": 1,
        "lawsuit": 1,
        "ipo": 2,
        "breakthrough": 1,
    }

    def score(
        self,
        event_type: str,
        description: str = "",
        company: str = "",
    ) -> int:
        base = self.BASE_SCORES.get(event_type, 3)
        text = (description or "").lower()

        modifier = 0
        for kw, weight in self.HIGH_IMPACT_KEYWORDS.items():
            if kw in text:
                modifier += weight

        # Cap the total between 1 and 10
        return max(1, min(10, base + modifier))