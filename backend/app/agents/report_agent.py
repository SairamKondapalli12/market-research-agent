"""Report Agent — synthesizes the final report."""

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from app.agents.base_agent import BaseAgent
from app.agents.prompts.report_prompts import (
    EXECUTIVE_SUMMARY_PROMPT,
    FULL_REPORT_PROMPT,
    RECOMMENDATIONS_PROMPT,
)
from app.database.crud import report_crud
from app.database.session import SessionLocal
from app.services.confidence_service import ConfidenceService
from app.utils.text_cleaner import TextCleaner


class ReportAgent(BaseAgent):
    def __init__(self, llm: Any = None, verbose: bool = False, request_id: str = None):
        super().__init__(
            name="report",
            role="Business Report Writer",
            goal="Synthesize intelligence into a structured executive report.",
            backstory="Analyst-report specialist with Fortune 500 client experience.",
            llm=llm,
            tools=[],
            verbose=verbose,
            request_id=request_id,
        )
        self.cleaner = TextCleaner()
        # Track LLM successes for confidence scoring
        self._llm_attempts = 0
        self._llm_successes = 0

    def _llm_text(self, prompt: str) -> str:
        self._llm_attempts += 1
        if self.llm is None:
            return ""
        try:
            response = self.llm.invoke(prompt)
            self._llm_successes += 1
            return response.content if hasattr(response, "content") else str(response)
        except Exception as exc:
            self.log(f"LLM error: {exc}", level="warning")
            return ""

    @property
    def _llm_success_rate(self) -> float:
        if self._llm_attempts == 0:
            return 1.0
        return self._llm_successes / self._llm_attempts

    @staticmethod
    def _parse_json(content: str) -> Dict[str, Any]:
        content = (content or "").strip()
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:]
        s, e = content.find("{"), content.rfind("}")
        if s == -1 or e == -1:
            return {}
        try:
            return json.loads(content[s : e + 1])
        except json.JSONDecodeError:
            return {}

    def _executive_summary(self, company_name, competitors, events):
        self.log("Composing executive summary", progress=88)
        if self.llm is None:
            top = events[:3]
            bullets = "\n".join(f"- {t['title']} ({t['company']})" for t in top)
            return (
                f"This report analyzes the competitive landscape around {company_name}. "
                f"It examines {len(competitors)} competitors and {len(events)} recent events.\n\n"
                f"Top developments:\n{bullets or '- No major events.'}"
            )
        events_text = "\n".join(
            f"- [{e['event_type']}] {e['company']}: {e['title']} (sig={e['significance']})"
            for e in events[:20]
        )
        prompt = EXECUTIVE_SUMMARY_PROMPT.format(
            company=company_name,
            competitor_count=len(competitors),
            events=events_text or "(no events)",
        )
        return self._llm_text(prompt).strip() or "Executive summary unavailable."

    def _recommendations(self, company_name, swot, events):
        self.log("Generating strategic recommendations", progress=92)
        if self.llm is None:
            return {
                "recommendations": [
                    "Monitor competitor product launches.",
                    "Invest in differentiation through innovation.",
                    "Strengthen customer retention programs.",
                ]
            }
        swot_text = json.dumps(swot, indent=2)[:3000]
        events_text = "\n".join(
            f"- [{e['event_type']}] {e['company']}: {e['title']}" for e in events[:15]
        )
        prompt = RECOMMENDATIONS_PROMPT.format(
            company=company_name, swot=swot_text, events=events_text
        )
        parsed = self._parse_json(self._llm_text(prompt))
        if "recommendations" not in parsed:
            parsed["recommendations"] = [
                "Monitor competitor activity",
                "Focus on differentiation",
            ]
        return parsed

    def _full_markdown(
        self,
        company_name,
        industry,
        competitors,
        events,
        swot,
        trends,
        executive_summary,
        recommendations,
        sentiment,
        financials,
    ):
        if self.llm is not None:
            prompt = FULL_REPORT_PROMPT.format(
                company=company_name,
                industry=industry or "N/A",
                competitors=json.dumps(competitors, indent=2)[:3000],
                events="\n".join(
                    f"- [{e['event_type']}] {e['company']}: {e['title']} (sig={e['significance']})"
                    for e in events[:30]
                ),
                swot=json.dumps(swot, indent=2)[:3000],
                trends=json.dumps(trends, indent=2)[:1500],
            )
            text = self._llm_text(prompt)
            if text.strip():
                return text.strip()

        lines = [
            f"# Market Research Report: {company_name}",
            f"_Generated: {datetime.now(timezone.utc).isoformat()}_",
            "",
            "## Executive Summary",
            executive_summary,
            "",
            "## Competitive Landscape",
        ]
        for c in competitors:
            lines.append(f"- **{c['name']}** — {c.get('description') or 'No description.'}")
        lines.append("\n## SWOT Analysis")
        for name, data in swot.items():
            lines.append(f"### {name}")
            for k in ("strengths", "weaknesses", "opportunities", "threats"):
                lines.append(f"**{k.title()}**:")
                for item in data.get(k, []) or []:
                    lines.append(f"- {item}")
            lines.append("")
        if financials:
            lines.append("## Financial Snapshot")
            for company, data in financials.items():
                lines.append(f"### {company}")
                if data.get("total_raised"):
                    lines.append(f"- Total Raised: {data['total_raised']}")
                if data.get("latest_valuation"):
                    lines.append(f"- Latest Valuation: {data['latest_valuation']}")
                if data.get("estimated_revenue"):
                    lines.append(f"- Estimated Revenue: {data['estimated_revenue']}")
                lines.append("")
        if sentiment:
            lines.append("## Market Sentiment")
            for company, data in sentiment.items():
                lines.append(
                    f"- **{company}**: {data.get('overall_label')} "
                    f"({data.get('overall_score')}) — {data.get('summary', '')}"
                )
            lines.append("")
        lines.append("## Market Trends")
        for t in trends.get("trends", []) or []:
            lines.append(f"- {t}")
        lines.append("\n## Recent Intelligence Events")
        for e in events[:25]:
            lines.append(
                f"- **[{e['event_type']}]** *{e['company']}* — {e['title']} (sig: {e['significance']}/10)"
            )
        lines.append("\n## Recommendations")
        for r in recommendations.get("recommendations", []) or []:
            lines.append(f"- {r}")
        return "\n".join(lines)

    def _one_pager_payload(self, company_name, executive_summary, events, recommendations):
        key_points: List[str] = []
        if executive_summary:
            key_points.append(executive_summary.split(".")[0].strip()[:120] + ".")
        for e in events[:3]:
            key_points.append(f"{e['company']}: {e['title'][:100]}")
        recs = recommendations.get("recommendations", [])[:3]
        return {
            "headline": f"Key insights on {company_name}",
            "key_points": key_points[:5] or ["No summary available."],
            "action": recs[0][:120] if recs else "Review the full report for details.",
        }

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        request_id = inputs["request_id"]
        company_name = inputs["company_name"]
        industry = inputs.get("industry")
        competitors = inputs.get("competitors", [])
        events = inputs.get("events", [])
        swot = inputs.get("swot", {})
        trends = inputs.get("trends", {})
        sentiment = inputs.get("sentiment", {})
        financials = inputs.get("financials", {})
        articles = inputs.get("articles", [])

        try:
            executive_summary = self._executive_summary(company_name, competitors, events)
            recommendations = self._recommendations(company_name, swot, events)
            full_md = self._full_markdown(
                company_name,
                industry,
                competitors,
                events,
                swot,
                trends,
                executive_summary,
                recommendations,
                sentiment,
                financials,
            )
            onepager = self._one_pager_payload(
                company_name, executive_summary, events, recommendations
            )

            # ─── Real confidence scoring ──────────────────────
            confidence = ConfidenceService.compute(
                articles=articles,
                events=events,
                competitors=competitors,
                sentiment=sentiment,
                financials=financials,
                llm_success_rate=self._llm_success_rate,
            )
            self.log(f"Computed confidence: {confidence}/100", progress=96)

            db = SessionLocal()
            try:
                report = report_crud.create(
                    db,
                    request_id=request_id,
                    title=f"Market Research Report: {company_name}",
                    executive_summary=executive_summary,
                    report_content=full_md,
                    swot_analysis=swot,
                    trends=trends,
                    recommendations=recommendations,
                    confidence_score=confidence,
                )
                report.sentiment_summary = sentiment or None
                report.financial_summary = financials or None
                report.onepager = onepager
                db.commit()
                db.refresh(report)
                report_id = str(report.id)
            finally:
                db.close()

            self.log(f"Report persisted (id={report_id})", progress=98)

            return {
                "success": True,
                "report": {
                    "id": report_id,
                    "title": f"Market Research Report: {company_name}",
                    "executive_summary": executive_summary,
                    "report_content": full_md,
                    "swot_analysis": swot,
                    "trends": trends,
                    "recommendations": recommendations,
                    "confidence_score": confidence,
                    "sentiment_summary": sentiment,
                    "financial_summary": financials,
                    "onepager": onepager,
                },
                "error": None,
            }
        except Exception as exc:
            self.log(f"Report agent failed: {exc}", level="error")
            return {"success": False, "report": None, "error": str(exc)}