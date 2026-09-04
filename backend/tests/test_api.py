"""Smoke tests for /health and core /api/v1 job flow with stubs."""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    from app.core.config import get_settings
    from app.jobs.store import store

    monkeypatch.setenv("ANIMAI_DATA_DIR", str(tmp_path))
    get_settings.cache_clear()
    from app.core import config

    config.settings = get_settings()
    config.settings.ensure_data_dirs()
    store.images.clear()
    store.jobs.clear()
    store.exports.clear()

    with TestClient(app) as c:
        yield c

    get_settings.cache_clear()


def _png_bytes(size=(64, 64)) -> bytes:
    buf = BytesIO()
    Image.new("RGB", size, color=(30, 144, 255)).save(buf, format="PNG")
    return buf.getvalue()


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_models(client: TestClient):
    r = client.get("/api/v1/models")
    assert r.status_code == 200
    models = r.json()["models"]
    assert any(m["id"] == "stub-detection" for m in models)


def test_process_flow(client: TestClient):
    upload = client.post(
        "/api/v1/images",
        files={"file": ("sample.png", _png_bytes(), "image/png")},
    )
    assert upload.status_code == 200
    image_id = upload.json()["id"]

    job = client.post("/api/v1/jobs/process", json={"image_id": image_id})
    assert job.status_code == 200
    body = job.json()
    assert body["status"] == "completed"
    job_id = body["id"]

    results = client.get(f"/api/v1/jobs/{job_id}/results")
    assert results.status_code == 200
    data = results.json()
    assert len(data["detections"]) >= 1
    assert len(data["masks"]) >= 1
    assert len(data["layers"]) >= 1

    export = client.post(
        f"/api/v1/jobs/{job_id}/export",
        json={"format": "json"},
    )
    assert export.status_code == 200
    assert export.json()["status"] == "ready"
    assert export.json()["download_url"]

    meta = client.get(f"/api/v1/exports/{export.json()['id']}")
    assert meta.status_code == 200
