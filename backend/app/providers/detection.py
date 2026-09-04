"""Stub object detection provider — deterministic fake boxes."""

from pathlib import Path

from app.providers.base import DetectionProvider
from app.schemas.common import BoundingBox
from app.schemas.jobs import Detection


class StubDetectionProvider(DetectionProvider):
    id = "stub-detection"
    name = "Stub Detection"

    def detect(self, image_path: Path, width: int, height: int) -> list[Detection]:
        # Deterministic layout relative to image size (no ML).
        w, h = float(width), float(height)
        return [
            Detection(
                id="det_character",
                label="character",
                confidence=0.94,
                bbox=BoundingBox(
                    x=w * 0.25, y=h * 0.15, width=w * 0.35, height=h * 0.7
                ),
            ),
            Detection(
                id="det_prop",
                label="prop",
                confidence=0.81,
                bbox=BoundingBox(
                    x=w * 0.62, y=h * 0.45, width=w * 0.2, height=h * 0.25
                ),
            ),
        ]
