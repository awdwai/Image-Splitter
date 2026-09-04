"""Helpers to write deterministic stub mask / layer PNGs."""

from pathlib import Path

from PIL import Image, ImageDraw


def write_rect_mask(
    path: Path,
    width: int,
    height: int,
    box: tuple[int, int, int, int],
    *,
    fill: int = 255,
) -> None:
    """Write a single-channel mask with a filled rectangle (deterministic)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(img)
    draw.rectangle(box, fill=fill)
    img.save(path, format="PNG")


def write_layer_rgba(
    path: Path,
    width: int,
    height: int,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int, int],
) -> None:
    """Write a translucent RGBA layer patch for demo exports."""
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle(box, fill=color)
    img.save(path, format="PNG")
