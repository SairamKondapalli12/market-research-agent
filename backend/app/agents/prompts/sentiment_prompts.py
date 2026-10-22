"""Prompt templates for the Sentiment Agent."""

SENTIMENT_ANALYSIS_PROMPT = """You are a market sentiment analyst.

Analyze the sentiment of the following text about {company} from a competitive intelligence perspective.

Text:
{text}

Consider:
- Positive signals: praise, adoption, growth, excitement, trust
- Negative signals: criticism, concerns, churn, setbacks, controversy
- Neutral signals: factual reporting without emotional tone

Return strict JSON:
{{
  "score": <float between -1.0 and 1.0>,
  "label": "positive" | "negative" | "neutral",
  "rationale": "<one concise sentence>"
}}

Score meanings:
- +1.0 = extremely positive
- +0.5 = clearly positive
-  0.0 = neutral
- -0.5 = clearly negative
- -1.0 = extremely negative

Return JSON only. No prose."""


SENTIMENT_AGGREGATE_PROMPT = """You are a market sentiment analyst.

Below are per-article sentiment results for {company}:

{items}

Produce an aggregate sentiment summary.

Return strict JSON:
{{
  "overall_score": <float -1.0 to 1.0>,
  "overall_label": "positive" | "negative" | "neutral",
  "distribution": {{
    "positive": <int>,
    "neutral": <int>,
    "negative": <int>
  }},
  "drivers": ["<key positive driver>", "<key negative driver>"],
  "summary": "<2-3 sentence narrative>"
}}

Return JSON only."""