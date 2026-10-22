"""Flexible date parsing for scraped content."""

from datetime import datetime, timezone
from typing import Optional

from dateutil import parser as dateutil_parser


class DateParser:

    FORMATS = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
        "%m/%d/%Y",
        "%d/%m/%Y",
    ]

    @classmethod
    def parse(cls, value: str) -> Optional[str]:
        """Return ISO-8601 date string, or None if parsing fails."""
        if not value:
            return None

        for fmt in cls.FORMATS:
            try:
                dt = datetime.strptime(value.strip(), fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.isoformat()
            except ValueError:
                continue

        try:
            dt = dateutil_parser.parse(value, fuzzy=True)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except Exception:
            return None

    @classmethod
    def to_datetime(cls, value: str) -> Optional[datetime]:
        iso = cls.parse(value)
        return datetime.fromisoformat(iso) if iso else None