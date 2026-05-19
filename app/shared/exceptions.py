from __future__ import annotations


class AppError(Exception):
    """Base for all application errors."""
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    """Resource not found, or caller has no access (404)."""
    pass


class ForbiddenError(AppError):
    """Caller is authenticated but not allowed to perform this action (403)."""
    pass


class ConflictError(AppError):
    """Resource already exists, e.g. duplicate email (409)."""
    pass


class ValidationError(AppError):
    """Business rule validation failed (422)."""
    pass


class UnauthorizedError(AppError):
    """Missing or invalid credentials (401)."""
    pass
