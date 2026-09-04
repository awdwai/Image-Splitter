"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends

from app.core.auth import require_api_key

RequireApiKey = Annotated[None, Depends(require_api_key)]
