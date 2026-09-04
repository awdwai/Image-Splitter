"""In-memory stores for images, jobs, and exports (swap for Redis/DB later)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Any
from uuid import uuid4

from app.core.errors import NotFoundError
from app.schemas.common import JobStatus, JobType, ExportFormat
from app.schemas.jobs import JobResults


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


@dataclass
class ImageRecord:
    id: str
    filename: str
    content_type: str
    width: int
    height: int
    path: str
    created_at: datetime = field(default_factory=_utcnow)


@dataclass
class JobRecord:
    id: str
    type: JobType
    status: JobStatus
    image_id: str
    progress: float = 0.0
    message: str | None = None
    error: str | None = None
    options: dict[str, Any] = field(default_factory=dict)
    model_id: str | None = None
    results: JobResults | None = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)


@dataclass
class ExportRecord:
    id: str
    job_id: str
    format: ExportFormat
    status: str
    path: str | None = None
    download_url: str | None = None
    error: str | None = None
    created_at: datetime = field(default_factory=_utcnow)


class InMemoryStore:
    """Thread-safe in-memory job/image/export registry."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.images: dict[str, ImageRecord] = {}
        self.jobs: dict[str, JobRecord] = {}
        self.exports: dict[str, ExportRecord] = {}

    def add_image(self, record: ImageRecord) -> ImageRecord:
        with self._lock:
            self.images[record.id] = record
            return record

    def get_image(self, image_id: str) -> ImageRecord:
        with self._lock:
            image = self.images.get(image_id)
            if not image:
                raise NotFoundError(f"Image not found: {image_id}")
            return image

    def add_job(self, record: JobRecord) -> JobRecord:
        with self._lock:
            self.jobs[record.id] = record
            return record

    def get_job(self, job_id: str) -> JobRecord:
        with self._lock:
            job = self.jobs.get(job_id)
            if not job:
                raise NotFoundError(f"Job not found: {job_id}")
            return job

    def update_job(self, job_id: str, **kwargs: Any) -> JobRecord:
        with self._lock:
            job = self.jobs.get(job_id)
            if not job:
                raise NotFoundError(f"Job not found: {job_id}")
            for key, value in kwargs.items():
                setattr(job, key, value)
            job.updated_at = _utcnow()
            return job

    def add_export(self, record: ExportRecord) -> ExportRecord:
        with self._lock:
            self.exports[record.id] = record
            return record

    def get_export(self, export_id: str) -> ExportRecord:
        with self._lock:
            export = self.exports.get(export_id)
            if not export:
                raise NotFoundError(f"Export not found: {export_id}")
            return export


store = InMemoryStore()
