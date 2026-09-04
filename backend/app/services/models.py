"""List selectable providers / models."""

from app.providers import list_models
from app.schemas.models import ModelsResponse


def get_models() -> ModelsResponse:
    return ModelsResponse(models=list_models())
