from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app import schemas
from db import models
from notifications.digest_builder import get_items_for_user

router = APIRouter(prefix="/api/users/{user_id}", tags=["items"])


def _get_user_or_404(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.get("/items", response_model=list[schemas.ItemRead])
def get_relevant_items(user_id: int, db: Session = Depends(get_db)):
    user = _get_user_or_404(db, user_id)

    items = get_items_for_user(db, user)

=    return items
