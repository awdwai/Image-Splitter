"""Image upload and registration."""

from pathlib import Path

from fastapi import UploadFile
from PIL import Image

from app.core.config import settings
from app.core.errors import BadRequestError
from app.jobs.store import ImageRecord, new_id, store
from app.schemas.images import ImageInfo

_ALLOWED = {
    "image/png",
    "image/jpeg",
    "image/jpg",
    "image/webp",
    "image/gif",
}


async def register_image(file: UploadFile) -> ImageInfo:
    settings.ensure_data_dirs()
    content_type = (file.content_type or "application/octet-stream").lower()
    if content_type not in _ALLOWED and not (file.filename or "").lower().endswith(
        (".png", ".jpg", ".jpeg", ".webp", ".gif")
    ):
        raise BadRequestError(
            "Unsupported image type",
            details={"content_type": content_type},
        )

    data = await file.read()
    if not data:
        raise BadRequestError("Empty upload")

    image_id = new_id("img")
    suffix = Path(file.filename or "upload.png").suffix or ".png"
    dest = settings.data_dir / "images" / f"{image_id}{suffix}"
    dest.write_bytes(data)

    try:
        with Image.open(dest) as im:
            width, height = im.size
            if content_type.startswith("application/") or content_type == "application/octet-stream":
                fmt = (im.format or "PNG").lower()
                content_type = f"image/{'jpeg' if fmt == 'jpeg' else fmt}"
    except Exception as exc:
        dest.unlink(missing_ok=True)
        raise BadRequestError("Could not decode image", details={"reason": str(exc)}) from exc

    record = ImageRecord(
        id=image_id,
        filename=file.filename or dest.name,
        content_type=content_type,
        width=width,
        height=height,
        path=str(dest),
    )
    store.add_image(record)
    return _to_schema(record)


def get_image(image_id: str) -> ImageInfo:
    return _to_schema(store.get_image(image_id))


def _to_schema(record: ImageRecord) -> ImageInfo:
    return ImageInfo(
        id=record.id,
        filename=record.filename,
        content_type=record.content_type,
        width=record.width,
        height=record.height,
        created_at=record.created_at,
        url=f"/api/v1/files/images/{Path(record.path).name}",
    )
