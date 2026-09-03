# AnimAI (Image-Splitter)

**AnimAI** is an AI image-decomposition platform. This repo contains two products:

| Product | Path | Role |
|---------|------|------|
| **Backend** | [`backend/`](backend/) | Reusable FastAPI API — the primary product |
| **Frontend** | [`frontend/`](frontend/) | One example web client that consumes the API |

## Products at a glance

### Backend (reusable API)

Use this alone from any client (web, CLI, Blender, scripts). Job-oriented REST under `/api/v1`, OpenAPI at `/docs`.

See [`backend/README.md`](backend/README.md) for install, env, and API-only quickstart.

### Frontend (example client)

A Vite React app that talks to the backend via `VITE_API_BASE_URL`. No AI/CV logic lives here — it only calls the API.

See [`frontend/README.md`](frontend/README.md).

## Quick start (both products)

Scaffold is in progress. Once Phase 2+ is complete:

```bash
# Terminal 1 — API
cd backend
# install + uvicorn (see backend/README.md)

# Terminal 2 — example UI
cd frontend
# npm install + npm run dev (see frontend/README.md)
```

Optional paired run via Docker Compose will be added in a later phase.

## License

MIT — see [LICENSE](LICENSE).
