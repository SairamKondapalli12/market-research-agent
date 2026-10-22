"""Auth middleware — attaches user context to request state."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Lightweight middleware that reads the Authorization header and
    stores the raw token in request.state for downstream use.
    Full validation happens in the dependency.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            request.state.token = auth_header[7:].strip()
        else:
            request.state.token = None
        return await call_next(request)