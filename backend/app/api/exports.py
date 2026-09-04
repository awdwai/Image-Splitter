"""Export fetch routes."""

from fastapi import APIRouter

from app.api.deps import RequireApiKey
from app.schemas.exports import ExportResponse
from app.services import exports as export_service

router = APIRouter()


@router.get(
    "/exports/{export_id}",
    response_model=ExportResponse,
    summary="Fetch export metadata / download URL",
)
def get_export(export_id: str, _: RequireApiKey) -> ExportResponse:
    return export_service.get_export(export_id)
