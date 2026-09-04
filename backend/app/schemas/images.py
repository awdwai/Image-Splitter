"""Image upload / registration schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class ImageInfo(BaseModel):
    """Registered image metadata returned after upload."""

    id: str
    filename: str
    content_type: str
    width: int
    height: int
    created_at: datetime
    url: str = Field(..., description="Relative URL to fetch the stored image")
