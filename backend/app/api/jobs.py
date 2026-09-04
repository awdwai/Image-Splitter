"""Job creation, status, results, corrections, and export-from-job routes."""

from fastapi import APIRouter

from app.api.deps import RequireApiKey
from app.schemas.exports import ExportRequest, ExportResponse
from app.schemas.jobs import (
    AnalyzeJobRequest,
    CorrectionRequest,
    JobResponse,
    JobResults,
    ProcessJobRequest,
    SegmentJobRequest,
)
from app.services import exports as export_service
from app.services import jobs as job_service

router = APIRouter()


@router.post(
    "/jobs/analyze",
    response_model=JobResponse,
    summary="Detect + pose + coarse analysis",
)
def start_analyze(body: AnalyzeJobRequest, _: RequireApiKey) -> JobResponse:
    return job_service.create_analyze_job(body)


@router.post(
    "/jobs/segment",
    response_model=JobResponse,
    summary="Segmentation / masks",
)
def start_segment(body: SegmentJobRequest, _: RequireApiKey) -> JobResponse:
    return job_service.create_segment_job(body)


@router.post(
    "/jobs/process",
    response_model=JobResponse,
    summary="Full decompose → layers",
)
def start_process(body: ProcessJobRequest, _: RequireApiKey) -> JobResponse:
    return job_service.create_process_job(body)


@router.post(
    "/jobs/{job_id}/corrections",
    response_model=JobResults,
    summary="Apply user mask/layer corrections",
)
def post_corrections(
    job_id: str, body: CorrectionRequest, _: RequireApiKey
) -> JobResults:
    return job_service.apply_corrections(job_id, body)


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    summary="Job status / progress",
)
def get_job(job_id: str, _: RequireApiKey) -> JobResponse:
    return job_service.get_job(job_id)


@router.get(
    "/jobs/{job_id}/results",
    response_model=JobResults,
    summary="Structured job results",
)
def get_results(job_id: str, _: RequireApiKey) -> JobResults:
    return job_service.get_results(job_id)


@router.post(
    "/jobs/{job_id}/export",
    response_model=ExportResponse,
    summary="Request export (PSD / PNG layers / JSON)",
)
def request_export(
    job_id: str, body: ExportRequest, _: RequireApiKey
) -> ExportResponse:
    return export_service.create_export(job_id, body)
