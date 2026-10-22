"""URL normalization and validation utilities."""

import re
from typing import Optional
from urllib.parse import urlparse, urlunparse


class URLValidator:

    SCHEME_RE = re.compile(r"^https?://", re.IGNORECASE)
    DOMAIN_RE = re.compile(
        r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$",
        re.IGNORECASE,
    )
    TRACKING_PARAMS = {
        "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
        "gclid", "fbclid", "mc_cid", "mc_eid", "ref", "source",
    }

    @classmethod
    def is_valid(cls, url: str) -> bool:
        if not url or not isinstance(url, str):
            return False
        if not cls.SCHEME_RE.match(url):
            return False
        try:
            parsed = urlparse(url)
            return bool(parsed.netloc and cls.DOMAIN_RE.match(parsed.netloc))
        except Exception:
            return False

    @classmethod
    def normalize(cls, url: str) -> Optional[str]:
        """Remove tracking params, fragment, and trailing slash."""
        if not cls.is_valid(url):
            return None
        parsed = urlparse(url)
        # Filter query params
        if parsed.query:
            params = [
                p for p in parsed.query.split("&")
                if p.split("=", 1)[0].lower() not in cls.TRACKING_PARAMS
            ]
            query = "&".join(params)
        else:
            query = ""
        path = parsed.path.rstrip("/") or "/"
        return urlunparse(
            (parsed.scheme, parsed.netloc.lower(), path, "", query, "")
        )

    @classmethod
    def domain(cls, url: str) -> Optional[str]:
        try:
            netloc = urlparse(url).netloc.lower()
            if netloc.startswith("www."):
                netloc = netloc[4:]
            return netloc or None
        except Exception:
            return None