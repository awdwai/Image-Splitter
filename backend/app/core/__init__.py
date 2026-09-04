"""Config, errors, auth, and logging."""

from app.core.config import settings
from app.core.errors import AnimAIError, ErrorCode

__all__ = ["settings", "AnimAIError", "ErrorCode"]
