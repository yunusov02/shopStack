
from typing import Generic, Optional, Sequence, Type, TypeVar

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel


ModelType = TypeVar("ModelType", bound=DeclarativeBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):


    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session


    async def get(self, id: UUID) -> ModelType | None:

        stmt = select(self.model).filter_by(id=id)
        result = await self.session.execute(stmt)

        return result.scalars().first()

    async def list(self) -> Sequence[ModelType]:

        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, entity: CreateSchemaType) -> ModelType:

        new_entity = self.model(**entity.dict())
        self.session.add(new_entity)
        await self.session.flush()  # Flush to get the ID of the new entity
        return new_entity


    async def update(self, id: UUID, entity: UpdateSchemaType) -> ModelType | None:

        exising_entity = await self.get(id)

        if not exising_entity:
            return None

        for key, value in entity.dict(exclude_unset=True).items(): # exclude unset fields to avoid overwriting existing values with None
            setattr(exising_entity, key, value)

        await self.session.flush()  # Flush to persist the changes
        return exising_entity


    async def delete(self, id: UUID) -> bool:

        entity = await self.get(id)

        if not entity:
            return False

        await self.session.delete(entity)
        await self.session.flush()  # Flush to persist the deletion
        return True

