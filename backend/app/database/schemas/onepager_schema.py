"""Pydantic schemas for the One-Pager."""

from typing import List

from pydantic import BaseModel


class OnePagerRead(BaseModel):
    report_id: str
    title: str
    headline: str
    key_points: List[str]
    action: str