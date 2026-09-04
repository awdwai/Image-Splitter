"""Shared schema enums and primitives."""

from enum import StrEnum

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class JobType(StrEnum):
    analyze = "analyze"
    segment = "segment"
    process = "process"


class ExportFormat(StrEnum):
    psd = "psd"
    png_layers = "png_layers"
    json = "json"


class BoundingBox(BaseModel):
    """Axis-aligned box in image pixel coordinates."""

    x: float = Field(..., description="Left edge")
    y: float = Field(..., description="Top edge")
    width: float
    height: float
