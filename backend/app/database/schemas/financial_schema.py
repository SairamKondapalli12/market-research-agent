"""Pydantic schemas for FinancialProfile."""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class FundingRoundRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    round_name: Optional[str] = None
    amount: Optional[str] = None
    amount_usd_millions: Optional[float] = None
    round_date: Optional[str] = None
    lead_investor: Optional[str] = None
    investors: Optional[List[str]] = None
    source_url: Optional[str] = None


class FinancialProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_id: uuid.UUID
    company: str
    total_raised: Optional[str] = None
    total_raised_millions: Optional[float] = None
    latest_valuation: Optional[str] = None
    estimated_revenue: Optional[str] = None
    investors: Optional[List[str]] = None
    financial_signals: Optional[List[str]] = None
    summary: Optional[str] = None
    funding_rounds: List[FundingRoundRead] = []
    created_at: datetime