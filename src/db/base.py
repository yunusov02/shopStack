from datetime import datetime


from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


from core.date_time import utc_now

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True



class SoftDeleteMixin(Base):
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: utc_now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now(), onupdate=utc_now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    