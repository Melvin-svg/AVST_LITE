from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/api/challenges", tags=["challenges"])


@router.get("", response_model=list[schemas.ChallengeOut])
def list_challenges(
    db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    challenges = db.query(models.Challenge).all()
    solved_ids = {
        s.challenge_id
        for s in db.query(models.Score).filter(models.Score.user_id == current_user.user_id)
    }
    result = []
    for c in challenges:
        out = schemas.ChallengeOut.model_validate(c)
        out.solved = c.challenge_id in solved_ids
        result.append(out)
    return result


@router.get("/{challenge_id}", response_model=schemas.ChallengeOut)
def get_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    challenge = db.query(models.Challenge).filter(models.Challenge.challenge_id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    out = schemas.ChallengeOut.model_validate(challenge)
    out.solved = (
        db.query(models.Score)
        .filter(
            models.Score.user_id == current_user.user_id,
            models.Score.challenge_id == challenge_id,
        )
        .first()
        is not None
    )
    return out


@router.post("/{challenge_id}/submit", response_model=schemas.FlagResult)
def submit_flag(
    challenge_id: int,
    payload: schemas.FlagSubmit,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    challenge = db.query(models.Challenge).filter(models.Challenge.challenge_id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")

    already_solved = (
        db.query(models.Score)
        .filter(
            models.Score.user_id == current_user.user_id,
            models.Score.challenge_id == challenge_id,
        )
        .first()
    )
    if already_solved:
        return schemas.FlagResult(correct=True, message="Already solved.", points_awarded=0)

    if challenge.check_flag(payload.flag):
        score = models.Score(
            user_id=current_user.user_id,
            challenge_id=challenge_id,
            score=challenge.points,
        )
        db.add(score)
        db.commit()
        return schemas.FlagResult(
            correct=True, message="Correct flag! Well done.", points_awarded=challenge.points
        )

    return schemas.FlagResult(correct=False, message="Incorrect flag. Try again.")
