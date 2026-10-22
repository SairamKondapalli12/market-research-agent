"""Pydantic schemas for Report Comparison."""

import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ReportCompareItem(BaseModel):
    id: uuid.UUID
    title: str
    company_name: str
    created_at: str
    confidence_score: Optional[int] = None
    executive_summary: Optional[str] = None
    competitors: List[str] = []
    top_events: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    sentiment: Optional[Dict[str, Any]] = None
    financials: Optional[Dict[str, Any]] = None


class ReportCompare(BaseModel):
    left: ReportCompareItem
    right: ReportCompareItem
    added_competitors: List[str] = []
    removed_competitors: List[str] = []
    common_competitors: List[str] = []
    new_recommendations: List[str] = []
    dropped_recommendations: List[str] = []
    common_recommendations: List[str] = []