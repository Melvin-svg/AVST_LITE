import hashlib
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    scores = relationship("Score", back_populates="user")


class Challenge(Base):
    __tablename__ = "challenges"

    challenge_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    points = Column(Integer, default=100)
    difficulty = Column(String, default="Easy")  # Easy, Medium, Hard, Insane
    flag_hash = Column(String, nullable=False)
    flag_format = Column(String, default="AVST{...}")
    hints = Column(Text, default="[]")  # JSON-encoded list of hint strings
    docker_lab = Column(String, nullable=True)  # key into docker labs, if any
    download_file = Column(String, nullable=True)  # filename served from challenge_files/

    scores = relationship("Score", back_populates="challenge")

    def check_flag(self, flag: str) -> bool:
        return hashlib.sha256(flag.strip().encode()).hexdigest() == self.flag_hash


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.challenge_id"), nullable=False)
    score = Column(Integer, default=0)
    solved_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="scores")
    challenge = relationship("Challenge", back_populates="scores")

    __table_args__ = (UniqueConstraint("user_id", "challenge_id", name="uq_user_challenge"),)
