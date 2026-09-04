"""Image upload routes."""

from fastapi import APIRouter, File, UploadFile

from app.api.deps import RequireApiKey
from app.schemas.images import ImageInfo
from app.services import images as image_service

router = APIRouter()


@router.post(
    "/images",
    response_model=ImageInfo,
    summary="Upload / register an image",
)
async def upload_image(
    _: RequireApiKey,
    file: UploadFile = File(..., description="Image file (PNG/JPEG/WebP/GIF)"),
) -> ImageInfo:
    return await image_service.register_image(file)
