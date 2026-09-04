"""Stub segmentation — rectangular masks written as PNGs."""

from pathlib import Path

from app.providers.base import SegmentationProvider
from app.providers.stubs_util import write_rect_mask
from app.schemas.jobs import Detection, MaskInfo


class StubSegmentationProvider(SegmentationProvider):
    id = "stub-segmentation"
    name = "Stub Segmentation"

    def segment(
        self,
        image_path: Path,
        width: int,
        height: int,
        detections: list[Detection],
        masks_dir: Path,
    ) -> list[MaskInfo]:
        masks: list[MaskInfo] = []
        for det in detections:
            b = det.bbox
            x0, y0 = int(b.x), int(b.y)
            x1, y1 = int(b.x + b.width), int(b.y + b.height)
            mask_id = f"mask_{det.id}"
            filename = f"{mask_id}.png"
            out = masks_dir / filename
            write_rect_mask(out, width, height, (x0, y0, x1, y1))
            masks.append(
                MaskInfo(
                    id=mask_id,
                    label=det.label,
                    score=round(det.confidence * 0.98, 3),
                    bbox=det.bbox,
                    mask_url=f"/api/v1/files/masks/{filename}",
                )
            )
        return masks
