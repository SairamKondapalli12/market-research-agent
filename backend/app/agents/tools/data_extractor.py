"""Data extraction utilities — pull structured info from raw text/HTML."""

import re
from typing import Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from app.utils.text_cleaner import TextCleaner


class DataExtractorTool:
    """Extracts structured pieces from unstructured web data."""

    COMPANY_SUFFIXES = {
        "inc", "inc.", "llc", "ltd", "ltd.", "corp", "corp.",
        "corporation", "co", "co.", "gmbh", "sa", "ag", "plc",
    }

    STOPWORDS = {
        # Generic words
        "the", "a", "an", "of", "for", "and", "or", "vs", "vs.",
        "top", "best", "leading", "review", "reviews", "guide",
        "2024", "2025", "2026", "news", "update",
        # Article-title fragments
        "who", "what", "when", "where", "why", "how",
        "facts", "fact", "list", "ways", "things",
        "alternatives", "competitors", "comparison", "compare",
        "surprising", "amazing", "popular", "rising",
        "hidden", "secret", "modern", "smart", "future",
        "startup", "startups", "platform", "platforms",
        "market", "industry", "sector", "business",
        "finding", "findings", "analysis", "insight", "insights",
        "report", "reports", "study", "research",
        "joins", "merges", "acquires", "partners", "partnership",
        "launch", "launches", "release", "releases",
        "landscape", "overview", "summary",
        "week", "month", "year", "today", "yesterday",
        "money", "valuation", "revenue", "growth", "funding",
    }

    def __init__(self):
        self.cleaner = TextCleaner()

    def extract_domain(self, url: str) -> Optional[str]:
        """Return the bare domain of a URL (e.g., 'example.com')."""
        try:
            netloc = urlparse(url).netloc.lower()
            if netloc.startswith("www."):
                netloc = netloc[4:]
            return netloc or None
        except Exception:
            return None

    def extract_competitor_name(self, title: str, exclude: str) -> Optional[str]:
        """
        Heuristically extract a competitor name from an article title.
        Rejects generic phrases, article-title fragments, and titles over 4 words.
        """
        if not title:
            return None

        exclude_lower = exclude.lower().strip()

        # Try "X vs Y" pattern
        vs_match = re.search(r"(.+?)\s+(?:vs\.?|versus)\s+(.+)", title, re.IGNORECASE)
        if vs_match:
            left, right = vs_match.group(1), vs_match.group(2)
            for candidate in (left, right):
                cand = candidate.strip(" -:,.")
                if not cand or cand.lower() == exclude_lower:
                    continue
                if len(cand) >= 60:
                    continue
                if len(cand.split()) > 4:
                    continue
                return self._clean_candidate(cand)

        # Skip generic "Alternatives to X" articles
        if re.search(r"alternatives?\s+to", title, re.IGNORECASE):
            return None

        # Skip "Top N X companies" articles
        if re.search(r"top\s+\d+", title, re.IGNORECASE):
            return None

        # Skip "X vs Y" articles we already handled — no other candidates
        if re.search(r"\bvs\.?\b", title, re.IGNORECASE):
            return None

        # Try 2-4 capitalized word sequences
        candidates = re.findall(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,3})\b", title)
        for cand in candidates:
            c = cand.strip()
            if c.lower() == exclude_lower:
                continue
            if c.lower() in self.STOPWORDS:
                continue
            if len(c) < 3 or len(c) > 60:
                continue
            if len(c.split()) > 4:
                continue
            # Reject if any word is a stopword
            words = c.lower().split()
            if any(w in self.STOPWORDS for w in words):
                continue
            cleaned = self._clean_candidate(c)
            if cleaned:
                return cleaned

        return None

    def _clean_candidate(self, name: str) -> str:
        tokens = name.split()
        while tokens and tokens[-1].lower().strip(",.") in self.COMPANY_SUFFIXES:
            tokens.pop()
        cleaned = " ".join(tokens).strip(" -:,.")
        if len(cleaned.split()) > 4:
            return ""
        return cleaned or name

    def extract_metadata(self, html: str) -> dict:
        """Extract metadata (title, description, author) from HTML."""
        try:
            soup = BeautifulSoup(html, "lxml")
        except Exception:
            return {}

        meta = {}
        if soup.title and soup.title.string:
            meta["title"] = soup.title.string.strip()

        for tag, key in [
            ('meta[name="description"]', "description"),
            ('meta[property="og:description"]', "description"),
            ('meta[name="author"]', "author"),
            ('meta[property="article:published_time"]', "published_date"),
        ]:
            el = soup.select_one(tag)
            if el and el.get("content"):
                meta.setdefault(key, el["content"].strip())

        return meta

    def extract_main_text(self, html: str) -> str:
        return self.cleaner.extract_main_text(html)