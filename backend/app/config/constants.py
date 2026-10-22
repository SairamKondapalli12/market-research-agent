"""Application-wide constants and enums."""

from enum import Enum


class ResearchStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResearchDepth(str, Enum):
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


class EventType(str, Enum):
    PRODUCT_LAUNCH = "product_launch"
    FUNDING = "funding"
    PARTNERSHIP = "partnership"
    ACQUISITION = "acquisition"
    HIRING = "hiring"
    PRICING_CHANGE = "pricing_change"
    LEADERSHIP_CHANGE = "leadership_change"
    EXPANSION = "expansion"
    LAYOFF = "layoff"
    LEGAL = "legal"
    MARKET_TREND = "market_trend"
    OTHER = "other"


class AgentType(str, Enum):
    MANAGER = "manager"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    REPORT = "report"


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class MonitoringFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class NotificationType(str, Enum):
    RESEARCH_COMPLETE = "research_complete"
    SIGNIFICANT_EVENT = "significant_event"
    WATCHLIST_UPDATE = "watchlist_update"
    ERROR = "error"


# ─── Research Depth Configuration ───────────────────────────────
RESEARCH_DEPTH_CONFIG = {
    ResearchDepth.QUICK: {
        "max_competitors": 3,
        "articles_per_competitor": 3,
        "search_depth": "basic",
        "max_iterations": 1,
    },
    ResearchDepth.STANDARD: {
        "max_competitors": 5,
        "articles_per_competitor": 5,
        "search_depth": "advanced",
        "max_iterations": 2,
    },
    ResearchDepth.DEEP: {
        "max_competitors": 8,
        "articles_per_competitor": 10,
        "search_depth": "advanced",
        "max_iterations": 3,
    },
}


# ─── Significance Thresholds ────────────────────────────────────
SIGNIFICANCE_THRESHOLDS = {
    "critical": 8,
    "high": 6,
    "medium": 4,
    "low": 1,
}


def get_significance_label(score: int) -> str:
    """Return a human-readable label for a significance score."""
    if score >= SIGNIFICANCE_THRESHOLDS["critical"]:
        return "critical"
    if score >= SIGNIFICANCE_THRESHOLDS["high"]:
        return "high"
    if score >= SIGNIFICANCE_THRESHOLDS["medium"]:
        return "medium"
    return "low"