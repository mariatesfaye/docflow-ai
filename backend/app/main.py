from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import documents, evaluation, health
from app.config import get_settings
from app.services.storage import ensure_storage_dirs


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    ensure_storage_dirs(settings)
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router, prefix="/api")
    app.include_router(documents.router, prefix="/api")
    app.include_router(evaluation.router, prefix="/api")
    return app


app = create_app()
