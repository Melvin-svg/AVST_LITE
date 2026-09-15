from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("", response_model=list[schemas.LeaderboardEntry])
def leaderboard(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    rows = (
        db.query(
            models.User.user_id,
            models.User.name,
            func.coalesce(func.sum(models.Score.score), 0).label("total_score"),
            func.count(models.Score.id).label("solved_count"),
        )
        .outerjoin(models.Score, models.Score.user_id == models.User.user_id)
        .group_by(models.User.user_id)
        .order_by(func.coalesce(func.sum(models.Score.score), 0).desc())
        .all()
    )
    return [
        schemas.LeaderboardEntry(
            user_id=r.user_id, name=r.name, total_score=r.total_score, solved_count=r.solved_count
        )
        for r in rows
    ]
