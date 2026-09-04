"""Pydantic request/response models — OpenAPI source of truth."""

from app.schemas.common import BoundingBox, JobStatus, JobType, ExportFormat
from app.schemas.images import ImageInfo
from app.schemas.jobs import (
    AnalyzeJobRequest,
    SegmentJobRequest,
    ProcessJobRequest,
    CorrectionRequest,
    JobResponse,
    JobResults,
    Detection,
    PoseResult,
    Keypoint,
    MaskInfo,
    LayerInfo,
)
from app.schemas.exports import ExportRequest, ExportResponse
from app.schemas.models import ModelInfo, ModelsResponse

__all__ = [
    "BoundingBox",
    "JobStatus",
    "JobType",
    "ExportFormat",
    "ImageInfo",
    "AnalyzeJobRequest",
    "SegmentJobRequest",
    "ProcessJobRequest",
    "CorrectionRequest",
    "JobResponse",
    "JobResults",
    "Detection",
    "PoseResult",
    "Keypoint",
    "MaskInfo",
    "LayerInfo",
    "ExportRequest",
    "ExportResponse",
    "ModelInfo",
    "ModelsResponse",
]
