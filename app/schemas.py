# app/schemas.py

from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


# ------------- User-related -------------

class UserCreate(BaseModel):
    email: EmailStr


class UserTopicsUpdate(BaseModel):
    topics: List[str] = Field(default_factory=list)


class UserLocationCreate(BaseModel):
    label: str
    address: str
    radius_miles: float = Field(gt=0, le=50)


class UserLocationRead(BaseModel):
    id: int
    label: Optional[str]
    address: str
    normalized_address: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    radius_miles: float

    class Config:
        orm_mode = True


class UserRead(BaseModel):
    user_id: int
    email: EmailStr
    interested_topics: List[str] = Field(default_factory=list)
    locations: List[UserLocationRead] = Field(default_factory=list)

    class Config:
        orm_mode = True


# ------------- Item-related -------------

class ItemRead(BaseModel):
    item_id: int
    item_title: Optional[str]
    case_code: Optional[str]
    topics_detected: List[str] = Field(default_factory=list)
    processed_summary: Optional[str]
    location: Optional[str]

    class Config:
        orm_mode = True


# ------------- Digest -------------

class DigestPreview(BaseModel):
    items: List[ItemRead]


class DigestSendResponse(BaseModel):
    status: str
    sent_to: EmailStr
    item_count: int
