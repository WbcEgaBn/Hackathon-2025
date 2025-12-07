# app/dependencies.py

from typing import Generator, List
from fastapi import Depends
from db.database import SessionLocal

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # CORS
    cors_origins: list[str] = ["*"]

    # Email
    email_host: str
    email_port: int
    email_username: str
    email_password: str

    # Example: database URL if you add it later
    # database_url: str = "sqlite:///./test.db"

    class Config:
        env_file = ".env"
        extra = "allow"  # allows extra env vars without crashing
  # ← OPTIONAL but useful so extra vars don’t crash the app

def get_settings():
    return Settings()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
