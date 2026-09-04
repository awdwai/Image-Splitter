"""Application error types and HTTP mapping."""

from enum import StrEnum

from fastapi import Request
from fastapi.responses import JSONResponse


class ErrorCode(StrEnum):
    NOT_FOUND = "not_found"
    VALIDATION = "validation_error"
    UNAUTHORIZED = "unauthorized"
    CONFLICT = "conflict"
    INTERNAL = "internal_error"
    BAD_REQUEST = "bad_request"


class AnimAIError(Exception):
    """Domain error raised by services; mapped to HTTP by the exception handler."""

    def __init__(
        self,
        message: str,
        *,
        code: ErrorCode = ErrorCode.INTERNAL,
        status_code: int = 500,
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class NotFoundError(AnimAIError):
    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(
            message,
            code=ErrorCode.NOT_FOUND,
            status_code=404,
            details=details,
        )


class BadRequestError(AnimAIError):
    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(
            message,
            code=ErrorCode.BAD_REQUEST,
            status_code=400,
            details=details,
        )


class UnauthorizedError(AnimAIError):
    def __init__(self, message: str = "Invalid or missing API key") -> None:
        super().__init__(
            message,
            code=ErrorCode.UNAUTHORIZED,
            status_code=401,
        )


async def animai_error_handler(_request: Request, exc: AnimAIError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )
