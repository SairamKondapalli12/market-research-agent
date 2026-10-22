"""Event classifier — categorizes text into intelligence event types."""

import re
from typing import Any, Dict, List

from app.config.constants import EventType


class EventClassifierTool:
    """
    Rule-based classifier that maps article text to one or more
    intelligence event types. Fast, deterministic, and dependency-free.
    """

    # Keyword patterns per event type (case-insensitive)
    PATTERNS: Dict[str, List[str]] = {
        EventType.PRODUCT_LAUNCH.value: [
            r"\blaunch(es|ed|ing)?\b",
            r"\bunveil(s|ed|ing)?\b",
            r"\bannounce[sd]? new\b",
            r"\brelease[sd]?\b",
            r"\bintroduc(es|ed|ing)\b",
        ],
        EventType.FUNDING.value: [
            r"\braise[sd]?\b",
            r"\bfunding round\b",
            r"\bseries [a-e]\b",
            r"\bseed round\b",
            r"\$\d+(?:\.\d+)?\s?(?:million|billion|m|b)\b",
            r"\bvaluation\b",
        ],
        EventType.PARTNERSHIP.value: [
            r"\bpartner(s|ed|ing|ship)?\b",
            r"\bcollaborat(e|es|ed|ion)\b",
            r"\balliance\b",
            r"\bjoint venture\b",
            r"\bteams? up with\b",
        ],
        EventType.ACQUISITION.value: [
            r"\bacqui(re|res|red|sition)\b",
            r"\bmerger\b",
            r"\bmerg(es|ed|ing)\b",
            r"\bbuy(s|ing)? out\b",
            r"\btakeover\b",
        ],
        EventType.HIRING.value: [
            r"\bhires?\b",
            r"\bappoint(s|ed|ment)?\b",
            r"\brecruits?\b",
            r"\bnew (ceo|cto|cfo|coo|vp|chief)\b",
            r"\bjoins? as\b",
        ],
        EventType.PRICING_CHANGE.value: [
            r"\bprice (increase|decrease|change|hike|cut)\b",
            r"\bpricing (update|change|model)\b",
            r"\braise[sd]? prices?\b",
            r"\bcut[s]? prices?\b",
        ],
        EventType.LEADERSHIP_CHANGE.value: [
            r"\b(ceo|cto|cfo|coo|president)\b.{0,30}\b(step(s)? down|resign(s|ed)?|depart(s|ed)?)\b",
            r"\bnew (ceo|cto|cfo|coo|president)\b",
        ],
        EventType.EXPANSION.value: [
            r"\bexpand(s|ed|ing|sion)\b",
            r"\bopens? (new )?(office|facility|store|location)\b",
            r"\benters? .{0,20} market\b",
        ],
        EventType.LAYOFF.value: [
            r"\blayoffs?\b",
            r"\bjob cuts?\b",
            r"\brestructur(e|es|ed|ing)\b",
        ],
        EventType.LEGAL.value: [
            r"\blawsuit\b",
            r"\bsue[sd]?\b",
            r"\blitigation\b",
            r"\bregulat(or|ion|ory)\b",
            r"\bfine[sd]?\b",
        ],
    }

    def classify(self, text: str, company: str) -> List[Dict[str, str]]:
        """
        Return a list of matched events (each with event_type + description).
        Multiple events may be returned for the same text.
        """
        if not text or len(text) < 30:
            return []

        lower = text.lower()
        matches: List[Dict[str, str]] = []

        for event_type, patterns in self.PATTERNS.items():
            for pat in patterns:
                m = re.search(pat, lower)
                if m:
                    # Extract a short snippet around the match
                    start = max(0, m.start() - 80)
                    end = min(len(text), m.end() + 120)
                    snippet = text[start:end].strip().replace("\n", " ")
                    matches.append(
                        {
                            "event_type": event_type,
                            "description": snippet,
                        }
                    )
                    break  # one match per event type is enough

        if not matches:
            # If nothing matched, don't fabricate — return empty
            return []

        return matches