"""HTTP routes only — validate in, call services, map errors out."""

from fastapi import APIRouter

from app.api import exports, files, images, jobs, models

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(images.router, tags=["images"])
api_router.include_router(jobs.router, tags=["jobs"])
api_router.include_router(exports.router, tags=["exports"])
api_router.include_router(models.router, tags=["models"])
api_router.include_router(files.router, tags=["files"])
