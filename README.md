# AnimAI (Image-Splitter)

**AnimAI** is an AI image-decomposition platform. This repo contains two products:

| Product | Path | Role |
|---------|------|------|
| **Backend** | [`backend/`](backend/) | Reusable FastAPI API — the primary product |
| **Frontend** | [`frontend/`](frontend/) | One example web client that consumes the API |

## Windows quick start

Double-click or run from a command prompt at the repo root:

| Script | What it does |
|--------|----------------|
| [`start.bat`](start.bat) | Sets up deps if needed, then opens backend + frontend in two new windows |
| [`start-backend.bat`](start-backend.bat) | Backend only (API /docs) — optional port: `start-backend.bat 8001` |
| [`start-frontend.bat`](start-frontend.bat) | Frontend only — optional API URL: `start-frontend.bat http://localhost:8001` |

If port **8000** is already in use, the scripts try **8001** and print a clear note (they do not kill other processes).

- Frontend: http://localhost:5173  
- API docs: http://localhost:8000/docs (or `:8001` if that fallback was used)

## Products at a glance

### Backend (reusable API)

Use this alone from any client (web, CLI, Blender, scripts). Job-oriented REST under `/api/v1`, OpenAPI at `/docs`.

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -e ".[dev]"
copy .env.example .env          # or cp
uvicorn app.main:app --reload --port 8000
```

See [`backend/README.md`](backend/README.md) and [`backend/docs/integration.md`](backend/docs/integration.md).

### Frontend (example client)

A Vite React app that talks to the backend via `VITE_API_BASE_URL`. No AI/CV logic lives here — it only calls the API.

```bash
cd frontend
copy .env.example .env          # or cp — optional
npm install
npm run dev
```

Open `http://localhost:5173`. See [`frontend/README.md`](frontend/README.md).

## Docker (optional)

Run both products together, or build/run the backend image alone.

```bash
# Both services (backend :8000, frontend :5173 → nginx)
docker compose up --build

# Backend only
docker build -t animai-backend ./backend
docker run --rm -p 8000:8000 animai-backend
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend URL baked into the frontend build (browser-reachable) |
| `FRONTEND_PORT` | `5173` | Host port for the frontend container |

Backend stays independent: local `uvicorn`, its own `Dockerfile`, or compose without the frontend service.

## License

MIT — see [LICENSE](LICENSE).
