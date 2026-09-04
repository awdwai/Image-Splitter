"""Selectable model / provider listing schemas."""

from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    id: str
    name: str
    kind: str = Field(
        ...,
        description="detection | pose | segmentation | inpainting | pipeline",
    )
    description: str
    available: bool = True
    is_stub: bool = True


class ModelsResponse(BaseModel):
    models: list[ModelInfo]
