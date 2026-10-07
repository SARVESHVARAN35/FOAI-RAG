# Ops Knowledge frontend

React and Vite frontend for the Enterprise IT Incident Knowledge RAG Assistant.
The assistant page is connected to the FastAPI RAG endpoint; other incident,
resolution, review, and knowledge workflows are clearly marked as unavailable
until their backend endpoints exist.

## Run locally

From this directory:

```powershell
npm install
npm run dev
```

Open the local URL printed by Vite (normally `http://localhost:5173`).

The backend runs separately from `../backend`:

```powershell
uvicorn app.main:app --reload
```

## Backend configuration

Set `VITE_API_BASE_URL` in `.env` to the FastAPI origin. The default is:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000
```

The frontend uses the backend's existing `POST /rag/query` and `GET /api/health`
routes. RAG status and answer content come from the backend unchanged. No
incident, resolution, review, or knowledge data is fabricated.

## Checks

```powershell
npm run lint
npm run build
npm audit
```
