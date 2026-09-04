"""Stub inpainting / layer builder — RGBA patches from masks."""

from pathlib import Path

from app.providers.base import InpaintingProvider
from app.providers.stubs_util import write_layer_rgba
from app.schemas.jobs import LayerInfo, MaskInfo

_COLORS = {
    "character": (80, 160, 255, 180),
    "prop": (255, 180, 60, 180),
    "background": (40, 40, 50, 120),
}


class StubInpaintingProvider(InpaintingProvider):
    id = "stub-inpainting"
    name = "Stub Inpainting / Layers"

    def cleanup_and_layers(
        self,
        image_path: Path,
        width: int,
        height: int,
        masks: list[MaskInfo],
        layers_dir: Path,
    ) -> list[LayerInfo]:
        layers: list[LayerInfo] = []

        # Background layer (full frame, low opacity tint)
        bg_name = "layer_background.png"
        write_layer_rgba(
            layers_dir / bg_name,
            width,
            height,
            (0, 0, width, height),
            _COLORS["background"],
        )
        layers.append(
            LayerInfo(
                id="layer_background",
                name="Background",
                kind="background",
                z_index=0,
                opacity=1.0,
                visible=True,
                image_url=f"/api/v1/files/layers/{bg_name}",
            )
        )

        for i, mask in enumerate(masks):
            if not mask.bbox:
                continue
            b = mask.bbox
            box = (int(b.x), int(b.y), int(b.x + b.width), int(b.y + b.height))
            color = _COLORS.get(mask.label, (200, 200, 200, 160))
            layer_id = f"layer_{mask.label}"
            filename = f"{layer_id}.png"
            write_layer_rgba(layers_dir / filename, width, height, box, color)
            layers.append(
                LayerInfo(
                    id=layer_id,
                    name=mask.label.title(),
                    kind=mask.label,
                    z_index=i + 1,
                    opacity=1.0,
                    visible=True,
                    mask_url=mask.mask_url,
                    image_url=f"/api/v1/files/layers/{filename}",
                )
            )
        return layers
