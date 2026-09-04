"""Export request/response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import ExportFormat


class ExportRequest(BaseModel):
    format: ExportFormat
    options: dict[str, Any] = Field(default_factory=dict)


class ExportResponse(BaseModel):
    id: str
    job_id: str
    format: ExportFormat
    status: str = Field(..., description="ready | pending | failed")
    download_url: str | None = None
    created_at: datetime
    error: str | None = None
