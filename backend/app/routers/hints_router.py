import json
import os
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/api/hints", tags=["hints"])

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")


def rule_based_hint(challenge: models.Challenge, hint_level: int) -> str:
    hints = json.loads(challenge.hints or "[]")
    if not hints:
        return "No hints are available for this challenge yet. Re-read the description carefully."
    index = min(hint_level - 1, len(hints) - 1)
    index = max(index, 0)
    return hints[index]


async def ollama_hint(challenge: models.Challenge, question: str, hint_level: int) -> Optional[str]:
    system_prompt = (
        "You are a cybersecurity teaching assistant for a CTF training platform. "
        "You NEVER reveal the flag or a full solution. You give progressive, "
        "Socratic hints that guide the student toward the concept they need to learn. "
        f"The current hint level is {hint_level} (higher = more direct, but still never the answer)."
    )
    prompt = (
        f"{system_prompt}\n\n"
        f"Challenge: {challenge.title} ({challenge.category})\n"
        f"Description: {challenge.description}\n"
        f"Student question: {question}\n\n"
        "Give one short, progressive hint (2-3 sentences max)."
    )
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(
                OLLAMA_URL,
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "").strip() or None
    except Exception:
        return None


@router.post("/{challenge_id}", response_model=schemas.HintResponse)
async def get_hint(
    challenge_id: int,
    payload: schemas.HintRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    challenge = db.query(models.Challenge).filter(models.Challenge.challenge_id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    ai_response = await ollama_hint(challenge, payload.question, payload.hint_level)
    if ai_response:
        return schemas.HintResponse(hint=ai_response, hint_level=payload.hint_level, source="ollama")

    fallback = rule_based_hint(challenge, payload.hint_level)
    return schemas.HintResponse(hint=fallback, hint_level=payload.hint_level, source="rule-based")
