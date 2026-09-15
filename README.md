# AVST Lite

AI-Assisted Cybersecurity Training Platform — see [AVST_Lite_BTech_Project.md](AVST_Lite_BTech_Project.md) for the full project brief.

## Project layout

```
backend/    FastAPI + SQLite API (auth, challenges, AI hints, CVE data, leaderboard)
frontend/   React (Vite) single-page app
docker/     Sample vulnerable labs (SQL Injection, XSS) used by Module 5
```

## Running the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. On first startup it auto-creates `avst_lite.db`
(SQLite) and seeds 5 sample challenges (Web, Crypto, Forensics, Reverse Engineering).

Interactive API docs: `http://127.0.0.1:8000/docs`

### AI Hint Assistant

The `/api/hints/{challenge_id}` endpoint tries a local [Ollama](https://ollama.com) model
first (`OLLAMA_URL`, default `http://localhost:11434/api/generate`, model `llama3` — override
with `OLLAMA_MODEL`). If Ollama isn't running, it automatically falls back to progressive,
rule-based hints stored per challenge — so the platform works even without a local LLM.

To enable real AI hints:

```bash
ollama serve
ollama pull llama3
```

## Running the frontend

Requires Node.js 18+.

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173`. It talks to the backend at `http://127.0.0.1:8000` by
default — override with a `.env` file containing `VITE_API_BASE=http://your-backend:8000`.

## Running the Docker labs (Module 5)

```bash
cd docker
docker compose up --build
```

- SQL Injection lab: `http://localhost:5001/lab/sqli-login`
- XSS lab: `http://localhost:5002/lab/xss-search`

These are intentionally vulnerable Flask apps for teaching purposes only — do not deploy
them outside an isolated lab environment.

## Default challenges

| Challenge | Category | Points |
|---|---|---|
| Login Bypass 101 | Web Security (SQLi) | 100 |
| Reflected Alert | Web Security (XSS) | 100 |
| Caesar's Secret | Cryptography | 75 |
| Hidden in Plain Sight | Forensics | 90 |
| Crack the Binary | Reverse Engineering | 120 |
