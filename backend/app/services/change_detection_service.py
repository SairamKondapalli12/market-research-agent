"""Change detection — finds the previous report for a company and computes the diff."""

import uuid
from typing import Optional

from app.config.logging_config import get_logger
from app.database.crud import diff_crud
from app.database.models.intelligence_event import IntelligenceEvent
from app.database.models.report import Report
from app.database.models.research_request import ResearchRequest
from app.database.session import SessionLocal
from app.services.diff_service import DiffService
from app.services.notification_service import create_notification

logger = get_logger(__name__)


class ChangeDetectionService:

    @staticmethod
    def _previous_report(db, current_report: Report) -> Optional[Report]:
        """Find the previous report for the same company, excluding the current one."""
        req = (
            db.query(ResearchRequest)
            .filter(ResearchRequest.id == current_report.request_id)
            .first()
        )
        if not req:
            return None

        return (
            db.query(Report)
            .join(ResearchRequest, Report.request_id == ResearchRequest.id)
            .filter(
                ResearchRequest.company_name == req.company_name,
                ResearchRequest.user_id == req.user_id,
                Report.id != current_report.id,
                Report.created_at < current_report.created_at,
            )
            .order_by(Report.created_at.desc())
            .first()
        )

    @staticmethod
    def detect(current_report_id: uuid.UUID) -> Optional[dict]:
        db = SessionLocal()
        try:
            current = db.query(Report).filter(Report.id == current_report_id).first()
            if not current:
                return None

            previous = ChangeDetectionService._previous_report(db, current)
            if not previous:
                logger.info(f"No previous report found for report {current_report_id}")
                return None

            # Gather events
            prev_events = (
                db.query(IntelligenceEvent)
                .filter(IntelligenceEvent.request_id == previous.request_id)
                .all()
            )
            curr_events = (
                db.query(IntelligenceEvent)
                .filter(IntelligenceEvent.request_id == current.request_id)
                .all()
            )

            diff_data = DiffService.compute(previous, current, prev_events, curr_events)

            # Persist diff
            diff = diff_crud.create(
                db,
                current_report_id=current.id,
                previous_report_id=previous.id,
                request_id=current.request_id,
                company_name=(current.title.split(":")[-1].strip() if current.title else "Unknown"),
                significance=diff_data["significance"],
                summary=diff_data["summary"],
                payload=diff_data,
            )

            # Notify user if significant
            if diff_data["significance"] >= 20:
                req = (
                    db.query(ResearchRequest)
                    .filter(ResearchRequest.id == current.request_id)
                    .first()
                )
                if req:
                    create_notification(
                        user_id=req.user_id,
                        type="significant_event",
                        title=f"Significant change detected: {req.company_name}",
                        body=diff_data["summary"][:180],
                        link=f"/reports/{current.id}/diff",
                    )

            return {
                "diff_id": str(diff.id),
                "significance": diff_data["significance"],
                "summary": diff_data["summary"],
            }
        except Exception as exc:
            logger.error(f"Change detection failed: {exc}")
            return None
        finally:
            db.close()