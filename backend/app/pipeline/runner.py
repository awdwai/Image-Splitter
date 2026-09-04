"""Pipeline runners that orchestrate providers into JobResults."""

from pathlib import Path

from app.jobs.store import ImageRecord
from app.providers import get_detection, get_pose, get_segmentation, get_inpainting
from app.schemas.jobs import Detection, JobResults, MaskInfo


def run_analyze(
    *,
    job_id: str,
    image: ImageRecord,
    masks_dir: Path,
    layers_dir: Path,
    model_id: str | None = None,
) -> JobResults:
    image_path = Path(image.path)
    detector = get_detection(model_id)
    pose_provider = get_pose(model_id)
    detections = detector.detect(image_path, image.width, image.height)
    pose = pose_provider.estimate_pose(
        image_path, image.width, image.height, detections
    )
    return JobResults(
        job_id=job_id,
        image_id=image.id,
        detections=detections,
        pose=pose,
        masks=[],
        layers=[],
        meta={"pipeline": "analyze", "providers": {"detection": detector.id, "pose": pose_provider.id}},
    )


def run_segment(
    *,
    job_id: str,
    image: ImageRecord,
    masks_dir: Path,
    layers_dir: Path,
    model_id: str | None = None,
    detection_ids: list[str] | None = None,
    prior_detections: list[Detection] | None = None,
) -> JobResults:
    image_path = Path(image.path)
    detector = get_detection(model_id)
    segmenter = get_segmentation(model_id)

    detections = prior_detections or detector.detect(
        image_path, image.width, image.height
    )
    if detection_ids:
        wanted = set(detection_ids)
        detections = [d for d in detections if d.id in wanted]

    masks = segmenter.segment(
        image_path, image.width, image.height, detections, masks_dir
    )
    return JobResults(
        job_id=job_id,
        image_id=image.id,
        detections=detections,
        pose=None,
        masks=masks,
        layers=[],
        meta={
            "pipeline": "segment",
            "providers": {"detection": detector.id, "segmentation": segmenter.id},
        },
    )


def run_process(
    *,
    job_id: str,
    image: ImageRecord,
    masks_dir: Path,
    layers_dir: Path,
    model_id: str | None = None,
) -> JobResults:
    image_path = Path(image.path)
    detector = get_detection(model_id)
    pose_provider = get_pose(model_id)
    segmenter = get_segmentation(model_id)
    inpainter = get_inpainting(model_id)

    detections = detector.detect(image_path, image.width, image.height)
    pose = pose_provider.estimate_pose(
        image_path, image.width, image.height, detections
    )
    masks: list[MaskInfo] = segmenter.segment(
        image_path, image.width, image.height, detections, masks_dir
    )
    layers = inpainter.cleanup_and_layers(
        image_path, image.width, image.height, masks, layers_dir
    )
    return JobResults(
        job_id=job_id,
        image_id=image.id,
        detections=detections,
        pose=pose,
        masks=masks,
        layers=layers,
        meta={
            "pipeline": "process",
            "providers": {
                "detection": detector.id,
                "pose": pose_provider.id,
                "segmentation": segmenter.id,
                "inpainting": inpainter.id,
            },
        },
    )
