# Database Schema

## users
| column | type | notes |
| --- | --- | --- |
| id | UUID | PK |
| email | VARCHAR(255) | UNIQUE |
| hashed_password | VARCHAR(255) | |
| full_name | VARCHAR(255) | nullable |
| is_active | BOOLEAN | default true |
| is_superuser | BOOLEAN | default false |
| gemini_api_key | VARCHAR(500) | nullable |
| tavily_api_key | VARCHAR(500) | nullable |
| email_notifications | BOOLEAN | default true |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

## research_requests, articles, intelligence_events, reports, competitors, watchlist
See `app/database/models/` for full column lists.