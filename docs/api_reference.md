# API Reference

Base URL: `/api/v1`

## Auth
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/login-json`
- `POST /auth/refresh?refresh_token=...`
- `GET  /auth/me`

## Research
- `POST   /research`
- `GET    /research`
- `GET    /research/{id}`
- `DELETE /research/{id}`
- `POST   /research/{id}/retry`

## Reports
- `GET /reports`
- `GET /reports/{id}`
- `GET /reports/{id}/export/markdown`

## Competitors
- `GET    /competitors`
- `GET    /competitors/{id}`
- `DELETE /competitors/{id}`

## Watchlist
- `GET    /watchlist`
- `POST   /watchlist`
- `PATCH  /watchlist/{id}`
- `DELETE /watchlist/{id}`

## Intelligence Feed
- `GET /feed?event_type=...&company=...&min_significance=...`

## Settings
- `GET /settings`
- `PUT /settings`