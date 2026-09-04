"""Job request/response and result schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import BoundingBox, JobStatus, JobType


class AnalyzeJobRequest(BaseModel):
    image_id: str
    model_id: str | None = Field(
        default=None, description="Optional detection/pose provider override"
    )
    options: dict[str, Any] = Field(default_factory=dict)


class SegmentJobRequest(BaseModel):
    image_id: str
    model_id: str | None = Field(
        default=None, description="Optional segmentation provider override"
    )
    detection_ids: list[str] | None = Field(
        default=None, description="Limit segmentation to prior detection IDs"
    )
    options: dict[str, Any] = Field(default_factory=dict)


class ProcessJobRequest(BaseModel):
    """Full decompose → layers pipeline."""

    image_id: str
    model_id: str | None = None
    options: dict[str, Any] = Field(default_factory=dict)


class JobResponse(BaseModel):
    id: str
    type: JobType
    status: JobStatus
    progress: float = Field(..., ge=0.0, le=1.0)
    image_id: str
    created_at: datetime
    updated_at: datetime
    error: str | None = None
    message: str | None = None


class Detection(BaseModel):
    id: str
    label: str
    confidence: float
    bbox: BoundingBox


class Keypoint(BaseModel):
    name: str
    x: float
    y: float
    confidence: float = 1.0


class PoseResult(BaseModel):
    keypoints: list[Keypoint]
    skeleton: list[list[str]] = Field(
        default_factory=list,
        description="Pairs of keypoint names forming bones",
    )


class MaskInfo(BaseModel):
    id: str
    label: str
    score: float
    bbox: BoundingBox | None = None
    mask_url: str | None = None


class LayerInfo(BaseModel):
    id: str
    name: str
    kind: str = Field(..., description="e.g. character, background, prop")
    z_index: int = 0
    opacity: float = 1.0
    visible: bool = True
    mask_url: str | None = None
    image_url: str | None = None


class JobResults(BaseModel):
    job_id: str
    image_id: str
    detections: list[Detection] = Field(default_factory=list)
    pose: PoseResult | None = None
    masks: list[MaskInfo] = Field(default_factory=list)
    layers: list[LayerInfo] = Field(default_factory=list)
    meta: dict[str, Any] = Field(default_factory=dict)


class MaskCorrection(BaseModel):
    id: str
    label: str | None = None
    mask_url: str | None = None
    bbox: BoundingBox | None = None
    deleted: bool = False


class LayerCorrection(BaseModel):
    id: str
    name: str | None = None
    visible: bool | None = None
    opacity: float | None = None
    z_index: int | None = None
    deleted: bool = False


class CorrectionRequest(BaseModel):
    """User edits applied on top of job results."""

    masks: list[MaskCorrection] | None = None
    layers: list[LayerCorrection] | None = None
    notes: str | None = None
