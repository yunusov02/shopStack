import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.api.router import api_router
from src.core.settings import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:

    try:
        logger.info("Starting up...")

        engine = create_async_engine(
            settings.database_url,
            echo=False,
        )

        app.state.engine = engine
        app.state.session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)

        yield
    finally:
        logger.info("Shutting down...")
        await app.state.engine.dispose()


def create_app() -> FastAPI:

    logger.info("Creating FastAPI app...")
    app = FastAPI(
        title="Shopstack ERP project", description="Shopstack ERP project", lifespan=lifespan
    )

    logger.info("Including API router...")
    app.include_router(api_router)

    return app
