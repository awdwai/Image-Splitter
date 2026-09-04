"""Stub pose estimation — deterministic keypoints on the main character box."""

from pathlib import Path

from app.providers.base import PoseProvider
from app.schemas.jobs import Detection, Keypoint, PoseResult


class StubPoseProvider(PoseProvider):
    id = "stub-pose"
    name = "Stub Pose"

    def estimate_pose(
        self, image_path: Path, width: int, height: int, detections: list[Detection]
    ) -> PoseResult | None:
        character = next((d for d in detections if d.label == "character"), None)
        if character is None and detections:
            character = detections[0]
        if character is None:
            return None

        b = character.bbox
        cx = b.x + b.width / 2
        top = b.y
        bottom = b.y + b.height

        keypoints = [
            Keypoint(name="head", x=cx, y=top + b.height * 0.08, confidence=0.95),
            Keypoint(name="neck", x=cx, y=top + b.height * 0.18, confidence=0.93),
            Keypoint(name="shoulder_l", x=b.x + b.width * 0.2, y=top + b.height * 0.28, confidence=0.9),
            Keypoint(name="shoulder_r", x=b.x + b.width * 0.8, y=top + b.height * 0.28, confidence=0.9),
            Keypoint(name="hip_l", x=b.x + b.width * 0.3, y=top + b.height * 0.55, confidence=0.88),
            Keypoint(name="hip_r", x=b.x + b.width * 0.7, y=top + b.height * 0.55, confidence=0.88),
            Keypoint(name="ankle_l", x=b.x + b.width * 0.35, y=bottom - b.height * 0.05, confidence=0.85),
            Keypoint(name="ankle_r", x=b.x + b.width * 0.65, y=bottom - b.height * 0.05, confidence=0.85),
        ]
        skeleton = [
            ["head", "neck"],
            ["neck", "shoulder_l"],
            ["neck", "shoulder_r"],
            ["shoulder_l", "hip_l"],
            ["shoulder_r", "hip_r"],
            ["hip_l", "ankle_l"],
            ["hip_r", "ankle_r"],
        ]
        return PoseResult(keypoints=keypoints, skeleton=skeleton)
