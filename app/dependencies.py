from typing import Generator, List
from fastapi import Depends
from db.database import SessionLocal

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    cors_origins: list[str] = ["*"]

    email_host: str
    email_port: int
    email_username: str
    email_password: str

    class Config:
        env_file = ".env"
        extra = "allow" 

def get_settings():
    return Settings()


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
