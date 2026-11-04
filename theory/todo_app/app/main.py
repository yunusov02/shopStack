import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import Base, engine
from app.db import models  # noqa: F401  # registers ORM models on Base.metadata
from app.api.tasks import router as tasks_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    logger.info("Start %s application", settings.app_name)
    yield
    engine.dispose()
    logger.info("Stop %s application", settings.app_name)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
    )

    @app.get("/")
    def read_base_page() -> str:
        return "Hello World"

    app.include_router(tasks_router)
    return app


app = create_app()
