"""Manager Agent — orchestrates the entire research pipeline."""

from typing import Any, Dict

from app.agents.analyst_agent import AnalystAgent
from app.agents.base_agent import BaseAgent
from app.agents.financial_agent import FinancialAgent
from app.agents.report_agent import ReportAgent
from app.agents.researcher_agent import ResearcherAgent
from app.agents.sentiment_agent import SentimentAgent
from app.config.constants import ResearchDepth, RESEARCH_DEPTH_CONFIG, ResearchStatus
from app.config.settings import settings
from app.database.crud import research_crud
from app.database.models.user import User
from app.database.session import SessionLocal
from app.services.activity_service import record as record_activity
from app.services.change_detection_service import ChangeDetectionService
from app.services.notification_service import create_notification


class ManagerAgent(BaseAgent):
    def __init__(self, llm: Any = None, verbose: bool = False, request_id: str = None):
        super().__init__(
            name="manager",
            role="Research Project Manager",
            goal="Oversee the research process and coordinate specialist agents.",
            backstory="Senior research director.",
            llm=llm,
            tools=[],
            verbose=verbose,
            request_id=request_id,
        )
        self.researcher = ResearcherAgent(llm=llm, verbose=verbose, request_id=request_id)
        self.analyst = AnalystAgent(llm=llm, verbose=verbose, request_id=request_id)
        self.sentiment = SentimentAgent(llm=llm, verbose=verbose, request_id=request_id) if settings.SENTIMENT_ENABLED else None
        self.financial = FinancialAgent(llm=llm, verbose=verbose, request_id=request_id)
        self.report_writer = ReportAgent(llm=llm, verbose=verbose, request_id=request_id)

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        request_id = inputs["request_id"]
        company_name = inputs["company_name"]
        depth = inputs.get("research_depth", ResearchDepth.STANDARD.value)
        user_id = inputs.get("user_id")

        self.log(f"Starting research for '{company_name}'", progress=5)

        db = SessionLocal()
        try:
            research_crud.update_status(db, request_id, ResearchStatus.PROCESSING.value, 5)
            depth_cfg = RESEARCH_DEPTH_CONFIG.get(
                ResearchDepth(depth), RESEARCH_DEPTH_CONFIG[ResearchDepth.STANDARD]
            )

            # ─── Phase 1: Discovery ─────────────────────────────
            self.log("Phase 1: discovering competitors and gathering sources", progress=10)
            research_crud.update_status(db, request_id, ResearchStatus.PROCESSING.value, 15)
            research_result = self.researcher.run({
                "request_id": request_id,
                "company_name": company_name,
                "industry": inputs.get("industry"),
                "known_competitors": inputs.get("known_competitors") or [],
                "max_competitors": depth_cfg["max_competitors"],
                "articles_per_competitor": depth_cfg["articles_per_competitor"],
                "search_depth": depth_cfg["search_depth"],
            })
            if not research_result.get("success"):
                raise RuntimeError(research_result.get("error", "Researcher failed"))
            competitors = research_result["competitors"]
            articles = research_result["articles"]
            self.log(
                f"Discovery complete — {len(competitors)} competitors, {len(articles)} articles",
                progress=45,
            )

            req = research_crud.get_by_id(db, request_id)
            if req:
                req.sources_count = len(articles)
                db.commit()

            # ─── Phase 2: Analysis ──────────────────────────────
            research_crud.update_status(db, request_id, ResearchStatus.PROCESSING.value, 50)
            analysis_result = self.analyst.run({
                "request_id": request_id,
                "company_name": company_name,
                "competitors": competitors,
                "articles": articles,
            })
            if not analysis_result.get("success"):
                raise RuntimeError(analysis_result.get("error", "Analyst failed"))
            events = analysis_result["events"]
            swot = analysis_result["swot"]
            trends = analysis_result["trends"]

            req = research_crud.get_by_id(db, request_id)
            if req:
                req.events_count = len(events)
                db.commit()

            # ─── Phase 2b: Sentiment (optional) ─────────────────
            sentiment_data: Dict[str, Any] = {}
            if self.sentiment is not None:
                sentiment_result = self.sentiment.run({
                    "request_id": request_id,
                    "company_name": company_name,
                    "competitors": competitors,
                    "articles": articles,
                })
                if sentiment_result.get("success"):
                    sentiment_data = sentiment_result.get("sentiment", {})

            # ─── Phase 2c: Financial Intelligence ───────────────
            financial_data: Dict[str, Any] = {}
            financial_result = self.financial.run({
                "request_id": request_id,
                "company_name": company_name,
                "competitors": competitors,
                "articles": articles,
            })
            if financial_result.get("success"):
                financial_data = financial_result.get("financials", {})

            # ─── Phase 3: Report ────────────────────────────────
            research_crud.update_status(db, request_id, ResearchStatus.PROCESSING.value, 80)
            report_result = self.report_writer.run({
                "request_id": request_id,
                "company_name": company_name,
                "industry": inputs.get("industry"),
                "competitors": competitors,
                "events": events,
                "swot": swot,
                "trends": trends,
                "sentiment": sentiment_data,
                "financials": financial_data,
                 "articles": articles, 
            })
            if not report_result.get("success"):
                raise RuntimeError(report_result.get("error", "Report agent failed"))

            research_crud.update_status(db, request_id, ResearchStatus.COMPLETED.value, 100)
            self.log("Pipeline complete", progress=100)

            report = report_result["report"]

            # ─── Change detection ───────────────────────────────
            try:
                ChangeDetectionService.detect(report["id"])
            except Exception as exc:
                self.log(f"Change detection skipped: {exc}", level="warning")

            # ─── Notify the user ────────────────────────────────
            if user_id:
                create_notification(
                    user_id=user_id,
                    type="research_complete",
                    title=f"{company_name} report is ready",
                    body=(
                        f"Generated {len(events)} events across {len(competitors)} competitors."
                    ),
                    link=f"/research/{request_id}/report",
                )

                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user and user.email_notifications:
                        import asyncio
                        from app.services.notification_service import NotificationService
                        asyncio.run(
                            NotificationService.send_research_complete(
                                to_email=user.email,
                                company_name=company_name,
                                report_title=report["title"],
                                report_url=f"http://localhost:3000/research/{request_id}/report",
                            )
                        )
                except Exception as exc:
                    self.log(f"Email skipped: {exc}", level="warning")

                record_activity(
                    action="research.completed",
                    actor="System",
                    user_id=user_id,
                    target_type="research",
                    target_id=str(request_id),
                    target_label=company_name,
                    level="success",
                )

            return {
                "success": True,
                "request_id": request_id,
                "report": report,
                "competitors": competitors,
                "events": events,
                "error": None,
            }

        except Exception as exc:
            self.log(f"Pipeline failed: {exc}", level="error")
            research_crud.update_status(
                db, request_id=request_id, status=ResearchStatus.FAILED.value,
                progress=0, error_message=str(exc),
            )
            if user_id:
                create_notification(
                    user_id=user_id,
                    type="error",
                    title=f"Research failed for {company_name}",
                    body=str(exc)[:200],
                )
                record_activity(
                    action="research.failed",
                    actor="System",
                    user_id=user_id,
                    target_type="research",
                    target_id=str(request_id),
                    target_label=company_name,
                    level="error",
                    detail=str(exc),
                )
            return {"success": False, "request_id": request_id, "report": None, "error": str(exc)}
        finally:
            db.close()