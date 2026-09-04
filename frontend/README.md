# AnimAI Frontend (example client)

Example **React + TypeScript + Vite** client for the AnimAI backend API.

This app contains **no AI/CV logic**. It only calls the reusable backend via `VITE_API_BASE_URL`.

## Requirements

- Node.js 20+ (or 18 LTS)
- A reachable AnimAI backend (default `http://localhost:8000`)

## Setup

```bash
cd frontend
cp .env.example .env   # optional — defaults already match local backend
npm install
npm run dev
```

Open the printed local URL (usually `http://localhost:5173`).

## Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend origin (no trailing slash required) |

See [`.env.example`](.env.example).

## App flow

1. Upload an image → `POST /api/v1/images`
2. Start full process → `POST /api/v1/jobs/process`
3. Poll status → `GET /api/v1/jobs/{id}`
4. Load masks/layers → `GET /api/v1/jobs/{id}/results`
5. Send layer corrections → `POST /api/v1/jobs/{id}/corrections`
6. Request export → `POST /api/v1/jobs/{id}/export`, then `GET /api/v1/exports/{id}`

Also uses `GET /health` and `GET /api/v1/models`.

## Layout

```
frontend/
├── src/
│   ├── api/           # Typed HTTP client
│   ├── components/    # Upload, progress, canvas, export
│   ├── hooks/         # Job polling + API health
│   ├── pages/         # Workspace UI
│   └── types/         # Mirrors backend schemas
├── .env.example
└── package.json
```

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Vite dev server |
| `npm run build` | Typecheck + production build |
| `npm run preview` | Preview production build |
| `npm run lint` | TypeScript check only |

## Docker

```bash
# From repo root (builds frontend with VITE_API_BASE_URL → localhost:8000)
docker compose up --build

# Frontend image alone (pass a browser-reachable API URL)
docker build -t animai-frontend --build-arg VITE_API_BASE_URL=http://localhost:8000 ./frontend
docker run --rm -p 5173:80 animai-frontend
```

## Backend

See [`../backend/README.md`](../backend/README.md) and OpenAPI at `http://localhost:8000/docs`.
