# Local Ollama FastAPI Demo

A minimal FastAPI demo that exposes a tiny web UI and endpoints to query a local Ollama LLM (Mistral).

## What it is

- Lightweight demo server that connects to Ollama via the `ollama` Python client.
- Provides synchronous and streamed responses for quick prototyping and local testing.

## Features

- Serves a single-page UI at `/` for entering prompts and viewing streamed responses.
- Health check at `/health` that verifies Ollama availability.
- Endpoints: `/generate`, `/ask`, and `/stream` for different interaction styles.
- Optional in-memory API-key credit tracking and `DEV_MODE` bypass for development.

## Files

- [backend/app.py](backend/app.py) — FastAPI server and endpoints.
- [backend/templates/index.html](backend/templates/index.html) — Minimal frontend that streams `/stream` responses.

## Requirements

- Python 3.10+
- Ollama running locally and reachable from this machine.

Install dependencies (from the `backend` folder):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

## Environment

Create a `.env` file (optional) with:

- `API_KEY` — single API key used by the server to validate requests (optional).
- `DEV_MODE` — set to `true` to bypass API key checks for development.

Example `.env`:

```
API_KEY=mysupersecretkey
DEV_MODE=false
```

Credits are tracked in memory in `backend/app.py` via `API_KEY_CREDITS` and are decreased per request (not persistent).

## Running

Start Ollama (must be running) then run the FastAPI app from the `backend` directory:

```bash
# in one terminal: (start ollama separately, if required)
# ollama serve

# in a second terminal:
cd backend
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000/` to use the web UI.

## Endpoints (quick)

- `GET /` — serves the frontend UI.
- `GET /health` — checks Ollama connectivity.
- `POST /generate` — body param `prompt` (form or JSON) returns full response.
- `POST /ask` — JSON payload `{ "prompt": "..." }` returns `answer` field.
- `POST /stream` — JSON payload `{ "prompt": "..." }` streams the response in small chunks as `text/plain`.

Example curl (non-streamed):

```bash
curl -X POST -H "Content-Type: application/json" -H "x-api-key: <KEY>" \
  -d '{"prompt":"Hello"}' http://127.0.0.1:8000/ask
```

## Notes

- This is intended for local prototyping and demos — not production-ready.
- API key credits live only in memory and reset on server restart.
- The UI stores the API key in `localStorage` if you enable `persist` in the page.

## License

MIT
