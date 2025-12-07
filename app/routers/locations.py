from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app import schemas
from db import models
from notifications.geocoder import geocode

router = APIRouter(prefix="/api/users/{user_id}/locations", tags=["locations"])


def _get_user_or_404(db: Session, user_id: int) -> models.User:
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.get("", response_model=list[schemas.UserLocationRead])
def list_locations(user_id: int, db: Session = Depends(get_db)):
    user = _get_user_or_404(db, user_id)
    return user.locations


@router.post("", response_model=schemas.UserLocationRead, status_code=status.HTTP_201_CREATED)
def add_location(
    user_id: int,
    payload: schemas.UserLocationCreate,
    db: Session = Depends(get_db),
):
    user = _get_user_or_404(db, user_id)

    geo = geocode(db, payload.address)

    loc = models.UserLocation(
        user_id=user.user_id,
        label=payload.label,
        address=payload.address,
        normalized_address=geo.get("normalized") if geo else payload.address,
        lat=float(geo["lat"]) if geo else None,
        lon=float(geo["lon"]) if geo else None,
        radius_miles=payload.radius_miles,
    )

    db.add(loc)
    db.commit()
    db.refresh(loc)

    return loc


@router.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_location(user_id: int, location_id: int, db: Session = Depends(get_db)):
    _ = _get_user_or_404(db, user_id)

    loc = (
        db.query(models.UserLocation)
        .filter(models.UserLocation.id == location_id,
                models.UserLocation.user_id == user_id)
        .first()
    )

    if not loc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found.")

    db.delete(loc)
    db.commit()
    return None
