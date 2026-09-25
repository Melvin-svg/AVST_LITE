from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


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
    difficulty: str = "Easy"
    flag_format: str = "AVST{...}"
    docker_lab: Optional[str] = None
    download_file: Optional[str] = None
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
    question: str = Field(..., min_length=1, max_length=1000)
    hint_level: int = Field(default=1, ge=1, le=3)


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
