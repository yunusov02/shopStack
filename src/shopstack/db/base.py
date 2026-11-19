import datetime
import uuid
from dataclasses import Field

from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import func


class Base(DeclarativeBase):

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default_factory=uuid.uuid4)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(default=None)


