"""Export request and download metadata."""

from app.core.config import settings
from app.core.errors import BadRequestError
from app.export import build_export
from app.jobs.store import ExportRecord, new_id, store
from app.schemas.common import JobStatus
from app.schemas.exports import ExportRequest, ExportResponse


def create_export(job_id: str, body: ExportRequest) -> ExportResponse:
    job = store.get_job(job_id)
    if job.status != JobStatus.completed or job.results is None:
        raise BadRequestError(
            "Export requires a completed job with results",
            details={"status": job.status},
        )

    export_id = new_id("exp")
    settings.ensure_data_dirs()
    path = build_export(
        export_id=export_id,
        results=job.results,
        fmt=body.format,
        exports_dir=settings.data_dir / "exports",
        data_dir=settings.data_dir,
    )
    filename = path.name
    record = ExportRecord(
        id=export_id,
        job_id=job_id,
        format=body.format,
        status="ready",
        path=str(path),
        download_url=f"/api/v1/files/exports/{filename}",
    )
    store.add_export(record)
    return _to_schema(record)


def get_export(export_id: str) -> ExportResponse:
    return _to_schema(store.get_export(export_id))


def _to_schema(record: ExportRecord) -> ExportResponse:
    return ExportResponse(
        id=record.id,
        job_id=record.job_id,
        format=record.format,
        status=record.status,
        download_url=record.download_url,
        created_at=record.created_at,
        error=record.error,
    )
