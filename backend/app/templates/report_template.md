# Market Research Report: {{ company_name }}

_Generated: {{ generated_at }}_

## Executive Summary

{{ executive_summary }}

## Competitive Landscape

{% for competitor in competitors %}
- **{{ competitor.name }}** — {{ competitor.description or 'No description available.' }}
  {% if competitor.website %}_Website: {{ competitor.website }}_{% endif %}
{% endfor %}

## SWOT Analysis

{% for name, swot in swot.items() %}
### {{ name }}

**Strengths**
{% for item in swot.strengths %}- {{ item }}
{% endfor %}

**Weaknesses**
{% for item in swot.weaknesses %}- {{ item }}
{% endfor %}

**Opportunities**
{% for item in swot.opportunities %}- {{ item }}
{% endfor %}

**Threats**
{% for item in swot.threats %}- {{ item }}
{% endfor %}

{% endfor %}

## Market Trends

{% for trend in trends.get('trends', []) %}
- {{ trend }}
{% endfor %}

## Recent Intelligence Events

{% for event in events[:30] %}
- **{{ event.event_type }}** — _{{ event.company }}_: {{ event.title }}
  (Significance: {{ event.significance }}/10)
{% endfor %}

## Recommendations

{% for rec in recommendations.get('recommendations', []) %}
- {{ rec }}
{% endfor %}