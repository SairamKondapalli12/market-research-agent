"""Financial service — retrieval helpers."""

import uuid
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.database.crud import financial_crud


class FinancialService:

    @staticmethod
    def get_for_request(db: Session, request_id: uuid.UUID) -> List[Dict[str, Any]]:
        profiles = financial_crud.list_by_request(db, request_id)
        out = []
        for p in profiles:
            out.append({
                "company": p.company,
                "total_raised": p.total_raised,
                "total_raised_millions": p.total_raised_millions,
                "latest_valuation": p.latest_valuation,
                "estimated_revenue": p.estimated_revenue,
                "investors": p.investors or [],
                "financial_signals": p.financial_signals or [],
                "summary": p.summary,
                "funding_rounds": [
                    {
                        "round": r.round_name,
                        "amount": r.amount,
                        "amount_usd_millions": r.amount_usd_millions,
                        "date": r.round_date,
                        "lead_investor": r.lead_investor,
                        "investors": r.investors or [],
                        "source_url": r.source_url,
                    }
                    for r in p.funding_rounds
                ],
            })
        return out