"""Model backend interfaces and stub implementations."""

from app.providers.base import (
    DetectionProvider,
    PoseProvider,
    SegmentationProvider,
    InpaintingProvider,
)
from app.providers.registry import list_models, get_detection, get_pose, get_segmentation, get_inpainting

__all__ = [
    "DetectionProvider",
    "PoseProvider",
    "SegmentationProvider",
    "InpaintingProvider",
    "list_models",
    "get_detection",
    "get_pose",
    "get_segmentation",
    "get_inpainting",
]
