from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.dependencies import get_settings

from app.routers import users, locations, items, digest


def create_app():
    app = FastAPI()

    settings = get_settings()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(users.router)     
    app.include_router(locations.router)  
    app.include_router(items.router)
    app.include_router(digest.router)

    return app


app = create_app()
