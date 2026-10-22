"""Prompt templates for the Researcher Agent."""

COMPETITOR_DISCOVERY_PROMPT = """Identify the top direct competitors of {company} in the {industry} space.

Consider:
- Similar product offerings
- Overlapping target markets
- Comparable business models

Return a comma-separated list of up to {max_competitors} competitor names only.
"""

ARTICLE_SUMMARY_PROMPT = """Summarize the following article about {company} in 2-3 sentences.

Article:
{article}

Focus on: product changes, funding, partnerships, market position.
"""