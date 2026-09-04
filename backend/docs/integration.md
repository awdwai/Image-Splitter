# AnimAI backend integration guide

Base URL (local): `http://localhost:8000`

Auth is **off** by default. If you set `ANIMAI_API_KEY`, send header `X-API-Key: <key>` on every `/api/v1` request.

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Typical flow

1. `POST /api/v1/images` — upload image → `image_id`
2. `POST /api/v1/jobs/process` (or `analyze` / `segment`) → `job_id`
3. `GET /api/v1/jobs/{id}` — poll status (stubs complete immediately)
4. `GET /api/v1/jobs/{id}/results` — detections, pose, masks, layers
5. Optional: `POST /api/v1/jobs/{id}/corrections`
6. `POST /api/v1/jobs/{id}/export` → `export_id` + `download_url`
7. `GET /api/v1/exports/{id}` — metadata; download via `download_url`

---

## curl

### Health

```bash
curl -s http://localhost:8000/health
```

### List models

```bash
curl -s http://localhost:8000/api/v1/models
```

### Upload image

```bash
curl -s -F "file=@./sample.png" http://localhost:8000/api/v1/images
```

Example response:

```json
{
  "id": "img_abc123",
  "filename": "sample.png",
  "content_type": "image/png",
  "width": 512,
  "height": 512,
  "created_at": "2026-09-03T12:00:00Z",
  "url": "/api/v1/files/images/img_abc123.png"
}
```

### Start full process job

```bash
curl -s -X POST http://localhost:8000/api/v1/jobs/process \
  -H "Content-Type: application/json" \
  -d '{"image_id":"img_abc123"}'
```

### Analyze only / segment only

```bash
curl -s -X POST http://localhost:8000/api/v1/jobs/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_id":"img_abc123"}'

curl -s -X POST http://localhost:8000/api/v1/jobs/segment \
  -H "Content-Type: application/json" \
  -d '{"image_id":"img_abc123","detection_ids":["det_character"]}'
```

### Status and results

```bash
curl -s http://localhost:8000/api/v1/jobs/job_abc123
curl -s http://localhost:8000/api/v1/jobs/job_abc123/results
```

### Corrections

```bash
curl -s -X POST http://localhost:8000/api/v1/jobs/job_abc123/corrections \
  -H "Content-Type: application/json" \
  -d '{
    "layers": [{"id":"layer_prop","visible":false}],
    "notes": "Hide prop for this shot"
  }'
```

### Export

```bash
# JSON results bundle
curl -s -X POST http://localhost:8000/api/v1/jobs/job_abc123/export \
  -H "Content-Type: application/json" \
  -d '{"format":"json"}'

# ZIP of PNG layers + masks
curl -s -X POST http://localhost:8000/api/v1/jobs/job_abc123/export \
  -H "Content-Type: application/json" \
  -d '{"format":"png_layers"}'

# PSD placeholder (JSON describing intended stack)
curl -s -X POST http://localhost:8000/api/v1/jobs/job_abc123/export \
  -H "Content-Type: application/json" \
  -d '{"format":"psd"}'

curl -s http://localhost:8000/api/v1/exports/exp_abc123
```

### With API key

```bash
curl -s http://localhost:8000/api/v1/models -H "X-API-Key: your-secret"
```

---

## Python (`httpx`)

```python
import httpx

BASE = "http://localhost:8000"
headers = {}  # or {"X-API-Key": "your-secret"}

with httpx.Client(base_url=BASE, headers=headers, timeout=60.0) as client:
    # Upload
    with open("sample.png", "rb") as f:
        image = client.post(
            "/api/v1/images",
            files={"file": ("sample.png", f, "image/png")},
        ).json()
    image_id = image["id"]

    # Process
    job = client.post(
        "/api/v1/jobs/process",
        json={"image_id": image_id},
    ).json()
    job_id = job["id"]
    assert job["status"] == "completed"

    results = client.get(f"/api/v1/jobs/{job_id}/results").json()
    print(len(results["detections"]), "detections,", len(results["layers"]), "layers")

    # Export JSON
    export = client.post(
        f"/api/v1/jobs/{job_id}/export",
        json={"format": "json"},
    ).json()
    print("download:", export["download_url"])
```

Install: `pip install httpx`

---

## JavaScript / TypeScript (`fetch`)

```ts
const BASE = "http://localhost:8000";
const headers: Record<string, string> = {
  // "X-API-Key": "your-secret",
};

async function run(file: File) {
  const form = new FormData();
  form.append("file", file);

  const image = await fetch(`${BASE}/api/v1/images`, {
    method: "POST",
    headers,
    body: form,
  }).then((r) => r.json());

  const job = await fetch(`${BASE}/api/v1/jobs/process`, {
    method: "POST",
    headers: { ...headers, "Content-Type": "application/json" },
    body: JSON.stringify({ image_id: image.id }),
  }).then((r) => r.json());

  const results = await fetch(`${BASE}/api/v1/jobs/${job.id}/results`, {
    headers,
  }).then((r) => r.json());

  const exportMeta = await fetch(`${BASE}/api/v1/jobs/${job.id}/export`, {
    method: "POST",
    headers: { ...headers, "Content-Type": "application/json" },
    body: JSON.stringify({ format: "png_layers" }),
  }).then((r) => r.json());

  return { image, job, results, exportMeta };
}
```

Point the example frontend at the same base via `VITE_API_BASE_URL=http://localhost:8000`.

---

## Error shape

Failed domain requests return:

```json
{
  "error": {
    "code": "not_found",
    "message": "Job not found: job_missing",
    "details": {}
  }
}
```

Common codes: `not_found`, `bad_request`, `unauthorized`, `validation_error`, `internal_error`.
