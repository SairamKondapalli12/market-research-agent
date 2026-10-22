from app.database.models.user import User
from app.database.models.research_request import ResearchRequest
from app.database.models.article import Article
from app.database.models.intelligence_event import IntelligenceEvent
from app.database.models.report import Report
from app.database.models.competitor import Competitor
from app.database.models.watchlist import Watchlist
from app.database.models.notification import Notification
from app.database.models.activity_log import ActivityLog
from app.database.models.share_link import ShareLink
from app.database.models.agent_log_event import AgentLogEvent

# ─── Feature expansion ─────────────────────────────────────
from app.database.models.sentiment_record import SentimentRecord
from app.database.models.chat_conversation import ChatConversation
from app.database.models.chat_message import ChatMessage
from app.database.models.research_schedule import ResearchSchedule
from app.database.models.report_diff import ReportDiff
from app.database.models.financial_profile import FinancialProfile
from app.database.models.funding_round import FundingRound
from app.database.models.investor import Investor

__all__ = [
    "User",
    "ResearchRequest",
    "Article",
    "IntelligenceEvent",
    "Report",
    "Competitor",
    "Watchlist",
    "Notification",
    "ActivityLog",
    "ShareLink",
    "AgentLogEvent",
    "SentimentRecord",
    "ChatConversation",
    "ChatMessage",
    "ResearchSchedule",
    "ReportDiff",
    "FinancialProfile",
    "FundingRound",
    "Investor",
]