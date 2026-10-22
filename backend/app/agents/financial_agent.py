"""Financial Intelligence Agent — extracts funding and valuation data."""

import json
from typing import Any, Dict, List

from app.agents.base_agent import BaseAgent
from app.agents.prompts.financial_prompts import (
    FINANCIAL_EXTRACTION_PROMPT,
    FINANCIAL_SUMMARY_PROMPT,
)
from app.agents.tools.financial_data_extractor import FinancialDataExtractorTool
from app.database.crud import financial_crud
from app.database.session import SessionLocal


class FinancialAgent(BaseAgent):
    MAX_ARTICLES_PER_COMPANY = 8
    # Anything above this threshold is considered nonsense
    MAX_PLAUSIBLE_RAISED_MILLIONS = 5_000_000  # $5T

    def __init__(self, llm: Any = None, verbose: bool = False, request_id: str = None):
        super().__init__(
            name="financial",
            role="Financial Intelligence Analyst",
            goal="Extract funding, valuation, and revenue signals per competitor.",
            backstory=(
                "You are a former venture capital analyst who has tracked "
                "hundreds of funding rounds. You are rigorous about "
                "distinguishing estimates from confirmed figures."
            ),
            llm=llm,
            tools=[],
            verbose=verbose,
            request_id=request_id,
        )
        self.extractor = FinancialDataExtractorTool()

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

    def _articles_for_company(
        self, company: str, articles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        needle = company.lower()
        return [
            a for a in articles
            if needle in ((a.get("title") or "") + (a.get("content") or "")).lower()
        ][: self.MAX_ARTICLES_PER_COMPANY]

    def _empty_financial_data(self) -> Dict[str, Any]:
        """Return a deterministic empty payload — used when we don't trust the data."""
        return {
            "funding_rounds": [],
            "total_raised": None,
            "total_raised_usd_millions": None,
            "latest_valuation": None,
            "estimated_revenue": None,
            "investors": [],
            "financial_signals": [],
        }

    def _sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Reject implausible numbers so we don't display garbage."""
        total = data.get("total_raised_usd_millions")
        if isinstance(total, (int, float)) and total > self.MAX_PLAUSIBLE_RAISED_MILLIONS:
            data["total_raised_usd_millions"] = None
            data["total_raised"] = None

        cleaned_rounds = []
        for r in data.get("funding_rounds", []) or []:
            amt = r.get("amount_usd_millions")
            if isinstance(amt, (int, float)) and amt > self.MAX_PLAUSIBLE_RAISED_MILLIONS:
                continue
            cleaned_rounds.append(r)
        data["funding_rounds"] = cleaned_rounds
        return data

    def _llm_extract(self, company: str, text: str) -> Dict[str, Any]:
        if self.llm is None:
            return self._empty_financial_data()

        prompt = FINANCIAL_EXTRACTION_PROMPT.format(company=company, text=text[:5000])
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, "content") else str(response)
            parsed = self._parse_json(content)
            if not parsed:
                return self._empty_financial_data()
            return self._sanitize(parsed)
        except Exception as exc:
            self.log(f"Financial LLM error: {exc}", level="warning")
            return self._empty_financial_data()

    def _summarize(self, company: str, data: Dict[str, Any]) -> str:
        if self.llm is None:
            parts = []
            if data.get("total_raised"):
                parts.append(f"Total raised: {data['total_raised']}.")
            if data.get("latest_valuation"):
                parts.append(f"Latest valuation: {data['latest_valuation']}.")
            if data.get("estimated_revenue"):
                parts.append(f"Estimated revenue: {data['estimated_revenue']}.")
            return " ".join(parts) or "No financial summary available."

        prompt = FINANCIAL_SUMMARY_PROMPT.format(
            company=company,
            rounds=json.dumps(data.get("funding_rounds", []), indent=2)[:2000],
            total_raised=data.get("total_raised") or "unknown",
            valuation=data.get("latest_valuation") or "unknown",
            revenue=data.get("estimated_revenue") or "unknown",
            investors=", ".join(data.get("investors", [])) or "unknown",
        )
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception:
            return "Financial summary unavailable."

    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        request_id = inputs["request_id"]
        company_name = inputs["company_name"]
        competitors = inputs.get("competitors", [])
        articles = inputs.get("articles", [])

        self.log("Extracting financial intelligence", progress=62)

        try:
            targets = [company_name] + [c["name"] for c in competitors]
            results: Dict[str, Any] = {}

            for target in targets:
                target_articles = self._articles_for_company(target, articles)
                if not target_articles:
                    continue

                combined = "\n\n".join(
                    (a.get("title") or "") + "\n" + (a.get("content") or "")
                    for a in target_articles
                )

                self.log(f"Extracting financials for {target}", progress=64)
                data = self._llm_extract(target, combined)
                summary = self._summarize(target, data)
                results[target] = {**data, "summary": summary}

            # Persist
            db = SessionLocal()
            try:
                for company, data in results.items():
                    financial_crud.create_profile(
                        db,
                        request_id=request_id,
                        company=company,
                        total_raised=data.get("total_raised"),
                        total_raised_millions=data.get("total_raised_usd_millions"),
                        latest_valuation=data.get("latest_valuation"),
                        estimated_revenue=data.get("estimated_revenue"),
                        investors=data.get("investors", []),
                        financial_signals=data.get("financial_signals", []),
                        summary=data.get("summary", ""),
                        funding_rounds=data.get("funding_rounds", []),
                    )
            finally:
                db.close()

            self.log("Financial intelligence complete", progress=64)
            return {"success": True, "financials": results, "error": None}

        except Exception as exc:
            self.log(f"Financial agent failed: {exc}", level="error")
            return {"success": False, "financials": {}, "error": str(exc)}