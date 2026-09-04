"""AnimAI FastAPI entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api import api_router
from app.core.config import settings
from app.core.errors import AnimAIError, animai_error_handler
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    settings.ensure_data_dirs()
    yield


app = FastAPI(
    title="AnimAI API",
    description=(
        "Reusable image analysis, segmentation, layering, and export API. "
        "Stub providers return deterministic fake masks/layers for local demos without a GPU."
    ),
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AnimAIError, animai_error_handler)
app.include_router(api_router)


@app.get("/health", tags=["health"], summary="Liveness")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "animai-backend", "version": __version__}
