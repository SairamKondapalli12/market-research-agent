"""Extracts financial signals from article text."""

import re
from typing import Any, Dict, List

AMOUNT_RE = re.compile(
    r"\$(\d+(?:\.\d+)?)\s*(million|billion|M|B)\b",
    re.IGNORECASE,
)

ROUND_RE = re.compile(
    r"\b(seed|pre-seed|series\s+[a-z]|ipo)\b",
    re.IGNORECASE,
)


class FinancialDataExtractorTool:
    """Rule-based extraction of funding amounts and rounds."""

    @staticmethod
    def amount_to_millions(amount_str: str, unit: str) -> float:
        value = float(amount_str)
        unit = unit.lower()
        if unit in ("billion", "b"):
            return value * 1000
        return value

    def extract_amounts(self, text: str) -> List[Dict[str, Any]]:
        results = []
        for match in AMOUNT_RE.finditer(text):
            amount, unit = match.group(1), match.group(2)
            millions = self.amount_to_millions(amount, unit)
            context_start = max(0, match.start() - 60)
            context_end = min(len(text), match.end() + 60)
            results.append({
                "raw": match.group(0),
                "usd_millions": millions,
                "context": text[context_start:context_end].strip().replace("\n", " "),
            })
        return results

    def extract_rounds(self, text: str) -> List[str]:
        rounds = set()
        for match in ROUND_RE.finditer(text):
            rounds.add(match.group(1).strip().title())
        return sorted(rounds)

    def extract(self, text: str) -> Dict[str, Any]:
        return {
            "amounts": self.extract_amounts(text),
            "rounds": self.extract_rounds(text),
        }