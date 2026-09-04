"""List selectable providers/models."""

from fastapi import APIRouter

from app.api.deps import RequireApiKey
from app.schemas.models import ModelsResponse
from app.services import models as model_service

router = APIRouter()


@router.get(
    "/models",
    response_model=ModelsResponse,
    summary="List selectable providers/models",
)
def list_models(_: RequireApiKey) -> ModelsResponse:
    return model_service.get_models()
