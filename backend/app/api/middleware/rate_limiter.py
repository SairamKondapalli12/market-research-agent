"""Simple in-memory rate limiter middleware."""

import time
from collections import defaultdict, deque
from typing import Deque, Dict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config.settings import settings


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Fixed-window rate limiter keyed by client IP.

    For production, use Redis-backed limiting. This implementation is
    dependency-free and sufficient for single-instance deployments.
    """

    def __init__(self, app, limit_per_minute: int = None):
        super().__init__(app)
        self.limit = limit_per_minute or settings.RATE_LIMIT_PER_MINUTE
        self.window = 60.0
        self._buckets: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip for docs / health
        path = request.url.path
        if path.startswith("/docs") or path.startswith("/redoc") or path in {"/", "/health"}:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        bucket = self._buckets[client_ip]
        # Drop timestamps outside the window
        while bucket and bucket[0] <= now - self.window:
            bucket.popleft()

        if len(bucket) >= self.limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."},
            )

        bucket.append(now)
        return await call_next(request)