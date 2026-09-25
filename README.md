# AVST Lite 🛡️

**AI-Assisted Cybersecurity Training Platform & Threat Intelligence Operations Center**

AVST Lite is a modern, hands-on cybersecurity training platform that combines interactive Capture-The-Flag (CTF) challenges, containerized exploit laboratories, real-time CVE threat intelligence feeds, and an AI-driven progressive hint assistant that coaches students through exploitation methodologies without spoiling solutions.

---

## 🌟 Key Features

- **Tactical CTF Arena**: 18 challenges covering **Web Security**, **Cryptography**, **Forensics**, and **Reverse Engineering** across four difficulty tiers (*Easy*, *Medium*, *Hard*, *Insane*).
- **Containerized Exploit Labs (Docker)**: Real, isolated, intentionally vulnerable web applications simulating real-world SQL Injection and Reflected Cross-Site Scripting (XSS).
- **Real-Time CVE Threat Intelligence**: Live telemetry ingestion from CISA's Known Exploited Vulnerabilities (KEV) Catalog and NIST NVD, featuring ransomware campaign vectors, 2026 zero-day exploits, and mitigation directives.
- **Adaptive AI Hint Advisor**: Local LLM-backed (Ollama / Llama 3) progressive coaching system with automatic fallback to structured tactical hints.
- **Cyberpunk Defense Operations UI**: Sleek, glassmorphic dark-theme command center with animated telemetry status, mission completion tracking, specialization readiness metrics, and an operative leaderboard with a podium showcase.

---

## 🏗️ Project Architecture

```
AVST_LITE/
├── backend/                  # FastAPI + SQLite API Service
│   ├── app/
│   │   ├── routers/          # Auth, Challenges, Hints, CVEs, Leaderboard
│   │   ├── database.py       # SQLAlchemy engine & SQLite session
│   │   ├── models.py         # User, Challenge, Submission, CVE models
│   │   ├── schemas.py        # Pydantic request/response schemas
│   │   ├── seed.py           # Auto-seeding for challenges & demo data
│   │   └── challenge_assets.py # Dynamic binary compilation & stego generator
│   ├── challenge_files/      # Generated download artifacts (PCAP, PNG, crackmes)
│   └── requirements.txt
├── frontend/                 # React 18 + Vite SPA
│   ├── src/
│   │   ├── api/              # Unified API client
│   │   ├── components/       # Navbar, AuthHero, ProtectedRoute
│   │   ├── context/          # JWT Auth Context & State
│   │   ├── pages/            # Dashboard, Challenges, Detail, CVE, Leaderboard, Auth
│   │   └── index.css         # Custom Cyberpunk design system & keyframe animations
│   └── package.json
└── docker/                   # Isolated Target Environments
    ├── docker-compose.yml    # Bridge network orchestration
    ├── sqli-lab/             # Vulnerable SQLi Staff Portal (Port 5001)
    └── xss-lab/              # Vulnerable Reflected XSS Query Portal (Port 5002)
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**
- **Docker** & **Docker Compose**
- *(Optional)* **Ollama** (for local LLM AI coaching)
- *(Optional)* A C compiler (`clang`, `gcc`, or `cc`) to compile Reverse Engineering crackmes at backend boot.

---

### 2. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- **API Base URL**: `http://localhost:8000`
- **Swagger / OpenAPI Documentation**: `http://localhost:8000/docs`
- **Automatic Initialization**: On first launch, the backend creates `avst_lite.db` (SQLite), seeds all 18 challenges, pre-populates real-time CVE intelligence, and dynamically compiles challenge artifacts into `backend/challenge_files/`.

---

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

- **Frontend Application**: `http://localhost:5173`
- Configured by default to communicate with `http://localhost:8000`. Set `VITE_API_BASE=http://your-host:8000` in a `.env` file to customize.

---

### 4. Running the Docker Target Labs

The platform includes isolated Docker environments for live exploit practice:

```bash
cd docker
docker compose up -d --build
```

| Container | Vulnerability | Local URL | Port |
|---|---|---|---|
| `docker-sqli-lab-1` | SQL Injection (Staff Login Bypass) | `http://localhost:5001/lab/sqli-login` | `5001` |
| `docker-xss-lab-1` | Reflected Cross-Site Scripting (XSS) | `http://localhost:5002/lab/xss-search` | `5002` |

> **Notes on Target Labs**:
> - Both labs include automatic root redirects (`/` redirects to the respective lab subpath).
> - The challenge interface includes **live container health detection**: it pings the local ports and dynamically alerts you if the target container is offline.
> - *These applications are intentionally vulnerable. Run them only in isolated environments.*

---

## 🎯 Challenges Breakdown

AVST Lite features **18 challenges** divided across four specializations and four difficulty tiers:

| Category | Easy | Medium | Hard | Insane |
|---|---|---|---|---|
| **Web Security** | Login Bypass 101 *(Docker)*<br>Reflected Alert *(Docker)* | Invoice Peeker *(IDOR)*<br>Forge the Token *(JWT)* | Internal Only *(SSRF)* | Blind Faith *(Time-based SQLi)* |
| **Cryptography** | Caesar's Secret *(Shift)* | Single Byte Shield *(XOR)* | Twin Primes *(RSA Fermat)* | Padding Oracle Whispers |
| **Forensics** | Hidden in Plain Sight *(Stego)* | Packet Secrets *(PCAP FTP)* | Deleted But Not Gone *(Carving)* | Memory Lane *(Memory Dump)* |
| **Reverse Engineering** | Crack the Binary *(Native)* | XOR Armor *(Deobfuscation)* | The Maze *(Multi-stage)* | Anti-Debug Fortress *(Anti-ptrace)* |

### Challenge Types:
1. **Interactive Docker Labs**: Hands-on targets hosted via local Docker containers (ports 5001 & 5002).
2. **Downloadable Artifacts**: Real files (PNG, PCAP, disk images, compiled ELF/Mach-O binaries) downloaded directly through the UI.
3. **Analytical & Conceptual Scenarios**: Real-world architectural scenarios (IDOR, JWT algorithm confusion, SSRF) solved by inspecting directives, analyzing token structures, and reasoning with the AI Advisor.

---

## 🤖 AI Hint Assistant Setup

The `/api/hints/{challenge_id}` endpoint utilizes a progressive clearance model (Levels 1–3) to guide users without giving away the flag.

1. **Local LLM via Ollama (Recommended)**:
   ```bash
   # Install and start Ollama (https://ollama.com)
   ollama serve
   ollama pull llama3
   ```
2. **Fallback Mode**: If Ollama is offline or unavailable, the backend automatically falls back to curated rule-based tactical hints stored per challenge.

---

## 🛡️ Live CVE Threat Intelligence Feed

The **CVE Intel Dashboard** integrates telemetry from public cybersecurity databases:
- **Live CISA KEV Sync**: Real-world exploited CVEs actively monitored by federal agencies.
- **Ransomware Threat Tracking**: Known ransomware attack vectors and historical zero-days.
- **Curated Remediation Guidance**: Actionable mitigation directives, CWE identifiers, and affected vendor mappings.
- **Lab Correlation**: Direct links connecting real-world CVEs with AVST Lite training labs.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy, SQLite, Pydantic, Passlib (bcrypt), python-jose (JWT), Uvicorn, httpx.
- **Frontend**: React 18, Vite, React Router DOM, JetBrains Mono & Inter typography, Vanilla CSS with custom glassmorphism design tokens.
- **Infrastructure**: Docker & Docker Compose.

---

## 📜 License & Usage

Created for educational and security training purposes. Ensure all exploit demonstrations and tools are conducted exclusively against the isolated local target environments provided in this repository.
