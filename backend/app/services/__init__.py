"""Services package.

Note: we intentionally avoid eager imports here to prevent circular
dependencies between the agents and service modules. Import services
directly from their module paths when you need them.

Example:
    from app.services.research_service import ResearchService
"""

__all__ = [
    "ResearchService",
    "ReportService",
    "MonitoringService",
    "NotificationService",
    "SemanticSearchService",
    "ConfidenceService",
    "CompareService",
    "ScheduleService",
    "RAGService",
    "EmbeddingService",
    "ActivityService",
    "AnalyticsService",
    "EventBusService",
]