# AnimAI Frontend (example client)

Example **React + TypeScript + Vite** client for the AnimAI backend API.

This is **not** the AI product — it only calls the reusable backend. Point it at any reachable API with `VITE_API_BASE_URL`.

## Status

Skeleton only (Phase 1). Full Vite app and UI land in a later phase.

## Layout

```
frontend/
└── src/
    ├── api/          # Typed HTTP client
    ├── pages/
    ├── components/
    ├── hooks/
    └── types/        # Mirrors backend schemas
```

## Environment

See [`.env.example`](.env.example):

```
VITE_API_BASE_URL=http://localhost:8000
```

## Planned usage (later)

```bash
# from frontend/
# npm install
# npm run dev
```

Requires the backend running (see [`../backend/README.md`](../backend/README.md)).
