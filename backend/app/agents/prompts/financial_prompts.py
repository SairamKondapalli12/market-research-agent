"""Prompt templates for the Financial Intelligence Agent."""

FINANCIAL_EXTRACTION_PROMPT = """You are a financial intelligence analyst.

Extract structured financial data about {company} from the text below.

Text:
{text}

Return strict JSON:
{{
  "funding_rounds": [
    {{
      "round": "<Seed|Series A|Series B|...>",
      "amount": "<e.g., $50M>",
      "amount_usd_millions": <float or null>,
      "date": "<YYYY-MM-DD or year>",
      "lead_investor": "<name or null>",
      "investors": ["<name>"],
      "source_url": "<url or null>"
    }}
  ],
  "total_raised": "<e.g., $250M>",
  "total_raised_usd_millions": <float or null>,
  "latest_valuation": "<e.g., $1.5B or null>",
  "estimated_revenue": "<e.g., $50M ARR or null>",
  "investors": ["<distinct investor name>"],
  "financial_signals": ["<other financial signal observed>"]
}}

If a field is unknown, use null. Return JSON only."""


FINANCIAL_SUMMARY_PROMPT = """You are a financial analyst.

Summarize the financial profile of {company} in 2-3 sentences using this data:

Funding rounds: {rounds}
Total raised: {total_raised}
Latest valuation: {valuation}
Estimated revenue: {revenue}
Investors: {investors}

Be concise and factual. No emojis. No markdown."""