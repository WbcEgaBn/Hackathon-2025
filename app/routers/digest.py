# app/routers/digest.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app import schemas
from db import models
from notifications.digest_builder import get_items_for_user
from notifications.email_renderer import render_digest
from notifications.email_sender import send_email

router = APIRouter(prefix="/api/users/{user_id}", tags=["digest"])


def _get_user_or_404(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.post("/send_digest", response_model=schemas.DigestSendResponse)
def send_digest(user_id: int, db: Session = Depends(get_db)):
    user = _get_user_or_404(db, user_id)
    items = get_items_for_user(db, user)

    if not items:
        raise HTTPException(status_code=404, detail="No matching items for this user.")

    html_body = render_digest(user, items)

    send_email(
        to=user.email,
        subject="Your Civic Agenda Digest",
        html_body=html_body,
    )

    return schemas.DigestSendResponse(
        status="sent",
        sent_to=user.email,
        item_count=len(items),
    )
