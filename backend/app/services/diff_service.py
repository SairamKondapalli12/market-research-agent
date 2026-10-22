"""Compute diffs between two reports for the same company."""

from typing import Any, Dict, List

from app.config.logging_config import get_logger

logger = get_logger(__name__)


class DiffService:

    @staticmethod
    def _competitor_names(report) -> set:
        """Extract competitor names from a report's swot_analysis JSON."""
        swot = report.swot_analysis or {}
        return {k for k in swot.keys()}

    @staticmethod
    def _recommendation_set(report) -> set:
        recs = (report.recommendations or {}).get("recommendations", [])
        return {r.strip() for r in recs if r}

    @staticmethod
    def _trend_set(report) -> set:
        trends = (report.trends or {}).get("trends", [])
        out = set()
        for t in trends:
            if isinstance(t, str):
                out.add(t.strip())
            elif isinstance(t, dict) and "name" in t:
                out.add(str(t["name"]).strip())
        return out

    @staticmethod
    def compute(previous, current, events_previous, events_current) -> Dict[str, Any]:
        """
        Compare two reports and return a structured diff payload.

        previous, current: Report ORM instances
        events_previous, events_current: List[IntelligenceEvent]
        """
        prev_comps = DiffService._competitor_names(previous)
        curr_comps = DiffService._competitor_names(current)
        added_comps = sorted(curr_comps - prev_comps)
        removed_comps = sorted(prev_comps - curr_comps)

        prev_recs = DiffService._recommendation_set(previous)
        curr_recs = DiffService._recommendation_set(current)
        new_recs = sorted(curr_recs - prev_recs)

        prev_trends = DiffService._trend_set(previous)
        curr_trends = DiffService._trend_set(current)
        new_trends = sorted(curr_trends - prev_trends)

        # New events (by title+company)
        prev_event_keys = {
            (e.company, (e.title or "")[:80]) for e in events_previous
        }
        new_events = [
            {
                "company": e.company,
                "event_type": e.event_type,
                "title": e.title,
                "significance": e.significance,
                "source_url": e.source_url,
            }
            for e in events_current
            if (e.company, (e.title or "")[:80]) not in prev_event_keys
        ]
        new_events.sort(key=lambda e: e["significance"], reverse=True)
        new_events = new_events[:15]

        # Significance score
        significance = min(
            100,
            len(added_comps) * 15
            + len(removed_comps) * 10
            + len(new_events) * 3
            + len(new_recs) * 5
            + len(new_trends) * 4,
        )

        summary_parts: List[str] = []
        if added_comps:
            summary_parts.append(f"{len(added_comps)} new competitor(s): {', '.join(added_comps[:3])}")
        if new_events:
            summary_parts.append(f"{len(new_events)} new intelligence event(s)")
        if new_recs:
            summary_parts.append(f"{len(new_recs)} new recommendation(s)")
        if not summary_parts:
            summary_parts.append("No material changes detected.")

        return {
            "added_competitors": added_comps,
            "removed_competitors": removed_comps,
            "new_events": new_events,
            "new_recommendations": new_recs,
            "trend_changes": new_trends,
            "summary": " ".join(summary_parts),
            "significance": significance,
        }