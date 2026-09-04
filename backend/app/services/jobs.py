"""Job creation, execution, status, results, and corrections."""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import settings
from app.core.errors import BadRequestError
from app.jobs.store import JobRecord, new_id, store
from app.pipeline import run_analyze, run_process, run_segment
from app.schemas.common import JobStatus, JobType
from app.schemas.jobs import (
    AnalyzeJobRequest,
    CorrectionRequest,
    JobResponse,
    JobResults,
    LayerInfo,
    MaskInfo,
    ProcessJobRequest,
    SegmentJobRequest,
)

logger = logging.getLogger(__name__)


def _to_response(job: JobRecord) -> JobResponse:
    return JobResponse(
        id=job.id,
        type=job.type,
        status=job.status,
        progress=job.progress,
        image_id=job.image_id,
        created_at=job.created_at,
        updated_at=job.updated_at,
        error=job.error,
        message=job.message,
    )


def _run_job(job_id: str, runner, **kwargs: Any) -> JobRecord:
    store.update_job(
        job_id,
        status=JobStatus.running,
        progress=0.1,
        message="Running pipeline",
    )
    try:
        settings.ensure_data_dirs()
        results = runner(
            job_id=job_id,
            masks_dir=settings.data_dir / "masks",
            layers_dir=settings.data_dir / "layers",
            **kwargs,
        )
        return store.update_job(
            job_id,
            status=JobStatus.completed,
            progress=1.0,
            message="Completed",
            results=results,
            error=None,
        )
    except Exception as exc:
        logger.exception("Job %s failed", job_id)
        return store.update_job(
            job_id,
            status=JobStatus.failed,
            progress=1.0,
            message="Failed",
            error=str(exc),
        )


def create_analyze_job(body: AnalyzeJobRequest) -> JobResponse:
    image = store.get_image(body.image_id)
    job = JobRecord(
        id=new_id("job"),
        type=JobType.analyze,
        status=JobStatus.queued,
        image_id=image.id,
        progress=0.0,
        message="Queued",
        options=body.options,
        model_id=body.model_id,
    )
    store.add_job(job)
    finished = _run_job(
        job.id,
        run_analyze,
        image=image,
        model_id=body.model_id,
    )
    return _to_response(finished)


def create_segment_job(body: SegmentJobRequest) -> JobResponse:
    image = store.get_image(body.image_id)
    job = JobRecord(
        id=new_id("job"),
        type=JobType.segment,
        status=JobStatus.queued,
        image_id=image.id,
        progress=0.0,
        message="Queued",
        options={**body.options, "detection_ids": body.detection_ids},
        model_id=body.model_id,
    )
    store.add_job(job)
    finished = _run_job(
        job.id,
        run_segment,
        image=image,
        model_id=body.model_id,
        detection_ids=body.detection_ids,
    )
    return _to_response(finished)


def create_process_job(body: ProcessJobRequest) -> JobResponse:
    image = store.get_image(body.image_id)
    job = JobRecord(
        id=new_id("job"),
        type=JobType.process,
        status=JobStatus.queued,
        image_id=image.id,
        progress=0.0,
        message="Queued",
        options=body.options,
        model_id=body.model_id,
    )
    store.add_job(job)
    finished = _run_job(
        job.id,
        run_process,
        image=image,
        model_id=body.model_id,
    )
    return _to_response(finished)


def get_job(job_id: str) -> JobResponse:
    return _to_response(store.get_job(job_id))


def get_results(job_id: str) -> JobResults:
    job = store.get_job(job_id)
    if job.status != JobStatus.completed or job.results is None:
        raise BadRequestError(
            "Results not available",
            details={"status": job.status, "error": job.error},
        )
    return job.results


def apply_corrections(job_id: str, body: CorrectionRequest) -> JobResults:
    job = store.get_job(job_id)
    if job.results is None:
        raise BadRequestError("Cannot correct a job without results")

    results = job.results.model_copy(deep=True)

    if body.masks:
        by_id = {m.id: m for m in results.masks}
        for corr in body.masks:
            if corr.deleted:
                by_id.pop(corr.id, None)
                continue
            existing = by_id.get(corr.id)
            if existing is None:
                by_id[corr.id] = MaskInfo(
                    id=corr.id,
                    label=corr.label or corr.id,
                    score=1.0,
                    bbox=corr.bbox,
                    mask_url=corr.mask_url,
                )
            else:
                if corr.label is not None:
                    existing.label = corr.label
                if corr.mask_url is not None:
                    existing.mask_url = corr.mask_url
                if corr.bbox is not None:
                    existing.bbox = corr.bbox
        results.masks = list(by_id.values())

    if body.layers:
        by_id = {layer.id: layer for layer in results.layers}
        for corr in body.layers:
            if corr.deleted:
                by_id.pop(corr.id, None)
                continue
            existing = by_id.get(corr.id)
            if existing is None:
                by_id[corr.id] = LayerInfo(
                    id=corr.id,
                    name=corr.name or corr.id,
                    kind="custom",
                    z_index=corr.z_index or 0,
                    opacity=corr.opacity if corr.opacity is not None else 1.0,
                    visible=corr.visible if corr.visible is not None else True,
                )
            else:
                if corr.name is not None:
                    existing.name = corr.name
                if corr.visible is not None:
                    existing.visible = corr.visible
                if corr.opacity is not None:
                    existing.opacity = corr.opacity
                if corr.z_index is not None:
                    existing.z_index = corr.z_index
        results.layers = list(by_id.values())

    if body.notes:
        results.meta = {**results.meta, "correction_notes": body.notes}

    store.update_job(job_id, results=results, message="Corrections applied")
    return results
