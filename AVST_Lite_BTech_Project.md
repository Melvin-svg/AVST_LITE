# AVST Lite – AI-Assisted Cybersecurity Training Platform

**A simplified B.Tech major project (KTU-friendly)**

---

## Abstract

AVST Lite is a simplified cybersecurity learning platform where students can practice Capture The Flag (CTF) challenges, receive AI-powered hints, and learn about real-world cyber vulnerabilities in a safe environment. Unlike the original AVST, which uses multiple AI agents and distributed systems, this version runs on a single laptop and focuses on five practical modules that can be completed within one semester.

---

# 1. Problem Statement

Many students struggle to learn practical cybersecurity because existing platforms are either too difficult for beginners or provide little guidance when they get stuck.

**Solution:** Build a web platform that combines beginner-friendly CTF challenges with an AI assistant that provides progressive hints instead of revealing answers.

---

# 2. Objectives

- Build a secure CTF learning platform.
- Provide AI-powered hints for students.
- Host vulnerable labs safely using Docker.
- Teach real-world vulnerabilities through CVEs.
- Track student progress with a leaderboard.

---

# 3. System Architecture

## Architecture Diagram

Student
   │
   ▼
React Web App
   │
   ▼
FastAPI Backend
   ├── AI Hint Assistant
   ├── Challenge Manager
   ├── CVE Learning Module
   └── Score System
   │
   ├── SQLite Database
   ├── Ollama AI
   └── Docker Containers

**Image suggestion:** Simple AI cybersecurity platform architecture diagram.

---

# 4. Core Modules

## Module 1 – Student Portal

Students can:

- Register
- Login
- View profile
- Track completed challenges

**Image suggestion:** Simple student login dashboard.

---

## Module 2 – CTF Challenge Portal

Students can solve challenges in categories such as:

- Web Security
- Cryptography
- Forensics
- Reverse Engineering

Each challenge contains:

- Description
- Downloadable files
- Flag submission
- Score

**Image suggestion:** CTF challenge page with flag submission.

---

## Module 3 – AI Hint Assistant (Main Innovation)

Instead of solving challenges automatically, the AI provides progressive hints.

Example:

Student:
> Why didn't my SQL Injection work?

AI:

- Hint 1: Check the login form.
- Hint 2: Try testing special characters.
- Hint 3: Learn about authentication bypass.

This encourages learning rather than simply revealing answers.

**Image suggestion:** AI chatbot helping a cybersecurity student.

---

## Module 4 – CVE Learning Section

A simple page introduces famous vulnerabilities.

| CVE | Description |
|------|------------|
| Log4Shell | Java vulnerability |
| EternalBlue | SMB exploit |
| Heartbleed | OpenSSL vulnerability |

Students can read about these attacks before attempting related challenges.

**Image suggestion:** CVE dashboard.

---

## Module 5 – Safe Docker Labs

Only practical web challenges run inside Docker containers.

Examples:

- SQL Injection Lab
- Cross-Site Scripting Lab
- File Upload Lab

Docker isolates every vulnerable application, making practice safe.

**Image suggestion:** Docker container architecture.

---

# 5. Technology Stack

| Component | Technology |
|------------|------------|
| Frontend | React |
| Backend | FastAPI |
| AI | Ollama (Llama 3 or Qwen) |
| Database | SQLite |
| Containers | Docker |
| Deployment | Render or Localhost |

SQLite is sufficient for a student project and keeps the setup simple.

---

# 6. Database Design

Only three main tables are needed.

## Users

- user_id
- name
- email
- password

## Challenges

- challenge_id
- title
- category
- points

## Scores

- user_id
- challenge_id
- score

Relationship:

Users → Scores ← Challenges

**Image suggestion:** Simple ER diagram.

---

# 7. User Workflow

1. Student logs in.
2. Dashboard opens.
3. Student selects a challenge.
4. Student asks the AI for hints.
5. Student submits the flag.
6. Leaderboard updates automatically.

**Image suggestion:** User flow diagram.

---

# 8. Expected Outcomes

The completed platform will allow students to:

- Practice cybersecurity safely.
- Learn through AI-guided hints.
- Understand real-world vulnerabilities.
- Compete with classmates.
- Build practical cybersecurity skills.

---

# 9. Four-Month Implementation Plan

| Month | Work |
|--------|------|
| Month 1 | Login, dashboard, SQLite setup |
| Month 2 | Challenge portal and Docker labs |
| Month 3 | AI Hint Assistant and CVE page |
| Month 4 | Leaderboard, testing, and deployment |

---

# 10. Future Enhancements

- Adaptive AI difficulty
- Mobile application
- Voice assistant
- Multiplayer CTF competitions
- Automatic challenge generation

---

# 11. Why This Version is Better for KTU

Compared to the original AVST, this version is realistic for a team of 3–4 students.

### Advantages

- Single-laptop setup
- Easy deployment
- Beginner-friendly implementation
- Strong AI feature
- Suitable for one-semester completion

The project still demonstrates modern technologies such as AI, Docker, FastAPI, and React while remaining manageable for a final-year B.Tech major project.

---

# Suggested Images

When converting this Markdown into a report or PDF, use these images:

1. Futuristic cybersecurity dashboard.
2. Simple AI architecture diagram.
3. Student login dashboard.
4. CTF challenge page.
5. AI chatbot helping a student.
6. CVE dashboard.
7. Docker container architecture.
8. ER diagram.
9. User workflow diagram.
10. Leaderboard interface.
