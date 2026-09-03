# AnimAI Backend

Reusable **FastAPI** API for AnimAI image analysis, segmentation, layering, and export.

This package is the primary product. You can run it without the frontend and integrate from any HTTP client.

## Status

Skeleton only (Phase 1). Routes, providers, and full quickstart land in later phases.

## Layout

```
backend/
├── app/
│   ├── api/         # HTTP routes
│   ├── schemas/     # Request/response models (OpenAPI)
│   ├── services/    # Use-cases / orchestration
│   ├── pipeline/    # Processing steps
│   ├── providers/   # Model backends (stubs → real)
│   ├── jobs/        # Job store + status
│   ├── export/      # Layer/export formats
│   └── core/        # Config, errors, auth, logging
├── docs/            # Integration guide + examples
└── tests/
```

## Planned usage (later)

```bash
# from backend/
# install deps via pyproject.toml
# copy .env.example → .env
# uvicorn app.main:app --reload --port 8000
```

- OpenAPI: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Environment

See [`.env.example`](.env.example). Optional `ANIMAI_API_KEY` for auth (disabled by default for local use).

## Integration

Integration examples (curl / Python / JS) will live under [`docs/`](docs/).
