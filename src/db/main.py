from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from core.settings import settings

async_engine = create_async_engine(settings.database_url, echo=settings.DEBUG, future=True)


async def get_async_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(async_engine) as session:
        yield session
