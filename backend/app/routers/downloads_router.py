from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .. import models
from ..auth import get_current_user
from ..challenge_assets import FILES_DIR
from ..database import get_db

router = APIRouter(prefix="/api/challenges", tags=["downloads"])


@router.get("/{challenge_id}/download")
def download_challenge_file(
    challenge_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    challenge = (
        db.query(models.Challenge)
        .filter(models.Challenge.challenge_id == challenge_id)
        .first()
    )
    if not challenge or not challenge.download_file:
        raise HTTPException(status_code=404, detail="No file for this challenge")

    # download_file is a fixed value from the seed data, never user input,
    # but resolve and confine to FILES_DIR as defence in depth.
    path = (FILES_DIR / challenge.download_file).resolve()
    if not str(path).startswith(str(FILES_DIR.resolve())) or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path,
        media_type="application/octet-stream",
        filename=challenge.download_file,
    )
