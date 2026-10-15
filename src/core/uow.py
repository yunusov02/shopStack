from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

class UnitOfWork:

    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:

        self._session_factory = sessionmaker
        self.session: AsyncSession | None = None


    async def __aenter__(self) -> "UnitOfWork":
        self.session = self._session_factory()
        return self



    async def __aexit__(
        self,
        exc_type: type[BaseException] | None, 
        exc: BaseException | None, 
        tb: TracebackType | None
    ) -> None:

        assert self.session is not None

        try:
            if exc_type is None:
                await self.session.commit()
            else:
                await self.session.rollback()
        finally:
            await self.session.close()




