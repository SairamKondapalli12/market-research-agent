"""Clean HTML → plain text for LLM consumption."""

import re
from typing import Optional

from bs4 import BeautifulSoup


class TextCleaner:

    WHITESPACE_RE = re.compile(r"\s+")
    SCRIPT_STYLE_TAGS = ["script", "style", "noscript", "iframe", "svg"]
    NAV_TAGS = ["nav", "header", "footer", "aside", "form"]

    def strip_html(self, html: str) -> str:
        """Remove all HTML tags and return plain text."""
        if not html:
            return ""
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(self.SCRIPT_STYLE_TAGS):
            tag.decompose()
        text = soup.get_text(separator="\n")
        return self.WHITESPACE_RE.sub(" ", text).strip()

    def extract_main_text(self, html: str, max_chars: int = 15000) -> str:
        """
        Extract the primary content of an HTML document.
        Tries <article> / <main> first, then falls back to body.
        """
        if not html:
            return ""
        try:
            soup = BeautifulSoup(html, "lxml")
        except Exception:
            return self.strip_html(html)

        for tag in soup(self.SCRIPT_STYLE_TAGS):
            tag.decompose()
        for tag in soup(self.NAV_TAGS):
            tag.decompose()

        container = (
            soup.find("article")
            or soup.find("main")
            or soup.find(attrs={"role": "main"})
            or soup.body
            or soup
        )
        text = container.get_text(separator="\n")
        text = self.WHITESPACE_RE.sub(" ", text).strip()
        return text[:max_chars]

    def clean_for_llm(self, text: str) -> str:
        """Normalize whitespace and truncate for LLM input."""
        if not text:
            return ""
        text = self.WHITESPACE_RE.sub(" ", text)
        text = re.sub(r"[^\x00-\x7F]+", " ", text)
        return text.strip()

    def truncate(self, text: str, max_chars: int = 8000) -> str:
        if not text or len(text) <= max_chars:
            return text or ""
        return text[:max_chars].rsplit(" ", 1)[0] + "..."