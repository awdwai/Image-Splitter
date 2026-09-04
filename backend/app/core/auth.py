"""Optional API-key authentication (off unless ANIMAI_API_KEY is set)."""

from typing import Annotated

from fastapi import Header, Security
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.core.errors import UnauthorizedError

API_KEY_HEADER_NAME = "X-API-Key"
_api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=False)


async def require_api_key(
    api_key: Annotated[str | None, Security(_api_key_header)] = None,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    """No-op when auth is disabled; otherwise require a matching X-API-Key."""
    if not settings.api_key_required:
        return
    provided = api_key or x_api_key
    if not provided or provided != settings.api_key:
        raise UnauthorizedError()
