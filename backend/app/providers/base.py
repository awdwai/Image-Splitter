"""Provider interfaces — swap stub implementations for real models later."""

from abc import ABC, abstractmethod
from pathlib import Path

from app.schemas.jobs import Detection, MaskInfo, PoseResult, LayerInfo


class DetectionProvider(ABC):
    id: str
    name: str

    @abstractmethod
    def detect(self, image_path: Path, width: int, height: int) -> list[Detection]:
        ...


class PoseProvider(ABC):
    id: str
    name: str

    @abstractmethod
    def estimate_pose(
        self, image_path: Path, width: int, height: int, detections: list[Detection]
    ) -> PoseResult | None:
        ...


class SegmentationProvider(ABC):
    id: str
    name: str

    @abstractmethod
    def segment(
        self,
        image_path: Path,
        width: int,
        height: int,
        detections: list[Detection],
        masks_dir: Path,
    ) -> list[MaskInfo]:
        ...


class InpaintingProvider(ABC):
    id: str
    name: str

    @abstractmethod
    def cleanup_and_layers(
        self,
        image_path: Path,
        width: int,
        height: int,
        masks: list[MaskInfo],
        layers_dir: Path,
    ) -> list[LayerInfo]:
        ...
