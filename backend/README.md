# AnimAI Backend

Reusable **FastAPI** API for AnimAI image analysis, segmentation, layering, and export.

This package is the primary product. You can run it without the frontend and integrate from any HTTP client (web, CLI, Blender, scripts).

## Quick start

```bash
cd backend

# Python 3.11+
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -e ".[dev]"
copy .env.example .env   # or: cp .env.example .env

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- OpenAPI UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json
- Health: http://localhost:8000/health

Stub providers return deterministic fake masks/layers so the API is demoable without a GPU.

## Layout

```
backend/
├── app/
│   ├── api/         # HTTP routes (thin)
│   ├── schemas/     # Request/response models (OpenAPI)
│   ├── services/    # Use-cases / orchestration
│   ├── pipeline/    # Processing steps
│   ├── providers/   # Model backends (stubs → real)
│   ├── jobs/        # In-memory job store
│   ├── export/      # Layer/export builders
│   ├── core/        # Config, errors, auth, logging
│   └── main.py      # FastAPI entry
├── docs/            # Integration guide + examples
└── tests/
```

Architecture: `api` → `services` → `pipeline` → `providers`. Jobs are stored in memory for the scaffold.

## Public API (`/api/v1`)

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/api/v1/images` | Upload / register image |
| `POST` | `/api/v1/jobs/analyze` | Detect + pose + coarse analysis |
| `POST` | `/api/v1/jobs/segment` | Segmentation / masks |
| `POST` | `/api/v1/jobs/process` | Full decompose → layers |
| `POST` | `/api/v1/jobs/{id}/corrections` | User mask/layer corrections |
| `GET` | `/api/v1/jobs/{id}` | Status / progress |
| `GET` | `/api/v1/jobs/{id}/results` | Structured results |
| `POST` | `/api/v1/jobs/{id}/export` | Request export (PSD/PNG layers/JSON) |
| `GET` | `/api/v1/exports/{id}` | Export metadata / download URL |
| `GET` | `/api/v1/models` | List selectable providers/models |
| `GET` | `/health` | Liveness |

Artifact downloads (images, masks, layers, exports) are under `/api/v1/files/...`.

## Environment

See [`.env.example`](.env.example).

| Variable | Default | Notes |
|----------|---------|-------|
| `ANIMAI_HOST` | `0.0.0.0` | Bind host (for docs; uvicorn CLI also sets host) |
| `ANIMAI_PORT` | `8000` | Port (docs; uvicorn CLI also sets port) |
| `ANIMAI_CORS_ORIGINS` | localhost Vite/React | Comma-separated |
| `ANIMAI_API_KEY` | _(empty)_ | If set, require `X-API-Key` header |
| `ANIMAI_DATA_DIR` | `./data` | Uploaded images, masks, layers, exports |
| `ANIMAI_JOB_STORE` | `memory` | Scaffold only |

## Example flow

```bash
# 1. Upload
curl -s -F "file=@sample.png" http://localhost:8000/api/v1/images

# 2. Full process (use image id from step 1)
curl -s -X POST http://localhost:8000/api/v1/jobs/process \
  -H "Content-Type: application/json" \
  -d "{\"image_id\":\"img_...\"}"

# 3. Results
curl -s http://localhost:8000/api/v1/jobs/JOB_ID/results
```

More curl / Python / JS examples: [`docs/integration.md`](docs/integration.md).

## Docker

```bash
# From repo root
docker build -t animai-backend ./backend
docker run --rm -p 8000:8000 animai-backend

# Or with the example frontend
docker compose up --build
```

## GPU / real models (future)

This scaffold ships stub providers only. Real SAM 2 / detector / pose weights will plug into `app/providers/` behind the same public schemas — no client API break expected.

## License

MIT — see the repository root `LICENSE`.
