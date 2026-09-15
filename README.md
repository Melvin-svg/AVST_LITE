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
(SQLite), seeds 18 challenges (Web, Crypto, Forensics, Reverse Engineering across
Easy/Medium/Hard/Insane), and generates the downloadable challenge artifacts into
`backend/challenge_files/`.

### Challenge artifacts

Forensics and reverse-engineering challenges ship real files students download and solve:

- **Forensics** — a stego PNG, a libpcap FTP capture, a raw disk image with a carvable
  deleted file, and a synthetic memory dump.
- **Reverse Engineering** — four native binaries compiled from C by the system compiler
  (`cc`/`clang`/`gcc`) at startup: a plain crackme, a static-XOR binary, a five-stage
  crackme, and an anti-debug fortress.

Every artifact is generated from the challenge's actual flag, so a correct solution always
matches the stored flag. The crypto challenges (Caesar, single-byte XOR, RSA/Fermat) embed
their ciphertext directly in the challenge description, and all decode cleanly to the flag.
Files are served (authenticated) from `GET /api/challenges/{id}/download`.

> If no C compiler is available, the four RE binaries are skipped but everything else still
> works. `backend/challenge_files/` is gitignored and rebuilt on each fresh startup.

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

## Challenges

18 challenges, 4-5 per category across four difficulty tiers:

| Category | Easy | Medium | Hard | Insane |
|---|---|---|---|---|
| Web Security | Login Bypass 101, Reflected Alert | Invoice Peeker, Forge the Token | Internal Only | Blind Faith |
| Cryptography | Caesar's Secret | Single Byte Shield | Twin Primes | Padding Oracle Whispers |
| Forensics | Hidden in Plain Sight | Packet Secrets | Deleted But Not Gone | Memory Lane |
| Reverse Engineering | Crack the Binary | XOR Armor | The Maze | Anti-Debug Fortress |

Every challenge shows its flag format (`AVST{...}`). Forensics/RE challenges provide a
download button; the two SQLi/XSS web challenges use the Docker labs; the remaining web
challenges are conceptual and walked through the AI assistant.
