"""Static file serving for uploaded images, masks, layers, and exports."""

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.api.deps import RequireApiKey
from app.core.config import settings
from app.core.errors import NotFoundError

router = APIRouter(prefix="/files")


def _safe_file(subdir: str, filename: str) -> FileResponse:
    # Prevent path traversal: only the basename under the known data subdir.
    safe_name = filename.replace("\\", "/").split("/")[-1]
    path = settings.data_dir / subdir / safe_name
    if not path.is_file():
        raise NotFoundError(f"File not found: {safe_name}")
    return FileResponse(path)


@router.get("/images/{filename}", summary="Download stored image")
def get_image_file(filename: str, _: RequireApiKey) -> FileResponse:
    return _safe_file("images", filename)


@router.get("/masks/{filename}", summary="Download mask PNG")
def get_mask_file(filename: str, _: RequireApiKey) -> FileResponse:
    return _safe_file("masks", filename)


@router.get("/layers/{filename}", summary="Download layer PNG")
def get_layer_file(filename: str, _: RequireApiKey) -> FileResponse:
    return _safe_file("layers", filename)


@router.get("/exports/{filename}", summary="Download export artifact")
def get_export_file(filename: str, _: RequireApiKey) -> FileResponse:
    return _safe_file("exports", filename)
