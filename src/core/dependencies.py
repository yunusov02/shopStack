from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.uow import UnitOfWork


async def get_session(request: Request) -> AsyncGenerator[AsyncSession]:

    async with request.app.state.async_session() as session:
        yield session


async def get_unit_of_work(request: Request) -> AsyncGenerator[UnitOfWork]:

    async with request.app.state.async_session() as session, UnitOfWork(session) as uow:
        yield uow


SessionDependency = Annotated[AsyncSession, Depends(get_session)]
UnitOfWorkDependency = Annotated[UnitOfWork, Depends(get_unit_of_work)]
