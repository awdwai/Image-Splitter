"""Provider registry — select stubs (or future real models) by id."""

from app.providers.detection import StubDetectionProvider
from app.providers.pose import StubPoseProvider
from app.providers.segmentation import StubSegmentationProvider
from app.providers.inpainting import StubInpaintingProvider
from app.providers.base import (
    DetectionProvider,
    PoseProvider,
    SegmentationProvider,
    InpaintingProvider,
)
from app.schemas.models import ModelInfo

_detection = StubDetectionProvider()
_pose = StubPoseProvider()
_segmentation = StubSegmentationProvider()
_inpainting = StubInpaintingProvider()

_DETECTION: dict[str, DetectionProvider] = {_detection.id: _detection}
_POSE: dict[str, PoseProvider] = {_pose.id: _pose}
_SEGMENTATION: dict[str, SegmentationProvider] = {_segmentation.id: _segmentation}
_INPAINTING: dict[str, InpaintingProvider] = {_inpainting.id: _inpainting}


def get_detection(model_id: str | None = None) -> DetectionProvider:
    if model_id and model_id in _DETECTION:
        return _DETECTION[model_id]
    return _detection


def get_pose(model_id: str | None = None) -> PoseProvider:
    if model_id and model_id in _POSE:
        return _POSE[model_id]
    return _pose


def get_segmentation(model_id: str | None = None) -> SegmentationProvider:
    if model_id and model_id in _SEGMENTATION:
        return _SEGMENTATION[model_id]
    return _segmentation


def get_inpainting(model_id: str | None = None) -> InpaintingProvider:
    if model_id and model_id in _INPAINTING:
        return _INPAINTING[model_id]
    return _inpainting


def list_models() -> list[ModelInfo]:
    return [
        ModelInfo(
            id=_detection.id,
            name=_detection.name,
            kind="detection",
            description="Deterministic fake bounding boxes for local demos (no GPU).",
            available=True,
            is_stub=True,
        ),
        ModelInfo(
            id=_pose.id,
            name=_pose.name,
            kind="pose",
            description="Deterministic fake skeleton on the primary detection.",
            available=True,
            is_stub=True,
        ),
        ModelInfo(
            id=_segmentation.id,
            name=_segmentation.name,
            kind="segmentation",
            description="Rectangular PNG masks derived from detections.",
            available=True,
            is_stub=True,
        ),
        ModelInfo(
            id=_inpainting.id,
            name=_inpainting.name,
            kind="inpainting",
            description="Builds demo RGBA layers from masks (no real inpainting).",
            available=True,
            is_stub=True,
        ),
        ModelInfo(
            id="stub-pipeline",
            name="Stub Full Pipeline",
            kind="pipeline",
            description="analyze → segment → layers using all stub providers.",
            available=True,
            is_stub=True,
        ),
    ]
