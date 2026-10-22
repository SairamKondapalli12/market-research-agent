"""CRUD for FinancialProfile, FundingRound, Investor."""

import uuid
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.database.models.financial_profile import FinancialProfile
from app.database.models.funding_round import FundingRound
from app.database.models.investor import Investor


def create_profile(
    db: Session,
    request_id: uuid.UUID,
    company: str,
    total_raised: Optional[str],
    total_raised_millions: Optional[float],
    latest_valuation: Optional[str],
    estimated_revenue: Optional[str],
    investors: Optional[List[str]],
    financial_signals: Optional[List[str]],
    summary: Optional[str],
    funding_rounds: Optional[List[Dict[str, Any]]] = None,
) -> FinancialProfile:
    profile = FinancialProfile(
        request_id=request_id,
        company=company,
        total_raised=total_raised,
        total_raised_millions=total_raised_millions,
        latest_valuation=latest_valuation,
        estimated_revenue=estimated_revenue,
        investors=investors,
        financial_signals=financial_signals,
        summary=summary,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    for r in funding_rounds or []:
        db.add(FundingRound(
            profile_id=profile.id,
            round_name=r.get("round"),
            amount=r.get("amount"),
            amount_usd_millions=r.get("amount_usd_millions"),
            round_date=r.get("date"),
            lead_investor=r.get("lead_investor"),
            investors=r.get("investors"),
            source_url=r.get("source_url"),
        ))

    for inv in investors or []:
        if not inv:
            continue
        db.add(Investor(profile_id=profile.id, name=inv))

    db.commit()
    db.refresh(profile)
    return profile


def list_by_request(db: Session, request_id: uuid.UUID) -> List[FinancialProfile]:
    return (
        db.query(FinancialProfile)
        .filter(FinancialProfile.request_id == request_id)
        .order_by(FinancialProfile.total_raised_millions.desc().nullslast())
        .all()
    )