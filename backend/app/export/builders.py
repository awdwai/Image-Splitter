"""Export builders for JSON, PNG layer zip, and PSD placeholder."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from app.core.errors import BadRequestError
from app.schemas.common import ExportFormat
from app.schemas.jobs import JobResults


def build_export(
    *,
    export_id: str,
    results: JobResults,
    fmt: ExportFormat,
    exports_dir: Path,
    data_dir: Path,
) -> Path:
    exports_dir.mkdir(parents=True, exist_ok=True)

    if fmt == ExportFormat.json:
        path = exports_dir / f"{export_id}.json"
        path.write_text(
            results.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return path

    if fmt == ExportFormat.png_layers:
        path = exports_dir / f"{export_id}_layers.zip"
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            manifest = {
                "job_id": results.job_id,
                "image_id": results.image_id,
                "layers": [layer.model_dump() for layer in results.layers],
                "masks": [mask.model_dump() for mask in results.masks],
            }
            zf.writestr("manifest.json", json.dumps(manifest, indent=2))
            for layer in results.layers:
                if layer.image_url:
                    filename = layer.image_url.rsplit("/", 1)[-1]
                    file_path = data_dir / "layers" / filename
                    if file_path.is_file():
                        zf.write(file_path, arcname=f"layers/{filename}")
            for mask in results.masks:
                if mask.mask_url:
                    filename = mask.mask_url.rsplit("/", 1)[-1]
                    file_path = data_dir / "masks" / filename
                    if file_path.is_file():
                        zf.write(file_path, arcname=f"masks/{filename}")
        return path

    if fmt == ExportFormat.psd:
        # Scaffold: PSD writer not wired; ship a JSON sidecar describing intended layers.
        path = exports_dir / f"{export_id}.psd.json"
        payload = {
            "format": "psd",
            "note": "PSD binary export is a stub; this JSON describes the intended layer stack.",
            "job_id": results.job_id,
            "layers": [layer.model_dump() for layer in results.layers],
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    raise BadRequestError(f"Unsupported export format: {fmt}")
