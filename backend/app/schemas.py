from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ChallengeOut(BaseModel):
    challenge_id: int
    title: str
    category: str
    description: str
    points: int
    docker_lab: Optional[str] = None
    solved: bool = False

    class Config:
        from_attributes = True


class FlagSubmit(BaseModel):
    flag: str


class FlagResult(BaseModel):
    correct: bool
    message: str
    points_awarded: int = 0


class HintRequest(BaseModel):
    question: str
    hint_level: int = 1


class HintResponse(BaseModel):
    hint: str
    hint_level: int
    source: str  # "ollama" or "rule-based"


class LeaderboardEntry(BaseModel):
    user_id: int
    name: str
    total_score: int
    solved_count: int


class CVEOut(BaseModel):
    cve_id: str
    name: str
    description: str
    year: int
    related_category: str
