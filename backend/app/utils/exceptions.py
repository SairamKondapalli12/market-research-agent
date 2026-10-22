"""Custom exception classes."""


class AppError(Exception):
    """Base application exception."""
    status_code = 500
    detail = "An unexpected error occurred."

    def __init__(self, detail: str = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = 404
    detail = "Resource not found."


class ValidationError(AppError):
    status_code = 422
    detail = "Invalid input."


class AuthenticationError(AppError):
    status_code = 401
    detail = "Authentication required."


class AuthorizationError(AppError):
    status_code = 403
    detail = "You do not have permission to perform this action."


class ExternalServiceError(AppError):
    status_code = 502
    detail = "An external service failed."


class ConfigurationError(AppError):
    status_code = 500
    detail = "The application is misconfigured."


class PipelineError(AppError):
    status_code = 500
    detail = "The research pipeline failed."