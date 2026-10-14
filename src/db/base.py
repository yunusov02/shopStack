from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql.sqltypes import DateTime

from core.settings import settings



class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(tz=settings.get_current_time())
    )


    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(tz=settings.get_current_time()),
        onupdate=lambda: datetime.now(tz=settings.get_current_time())
    )


    deleted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None
    )

    is_deleted: Mapped[bool] = mapped_column(
        nullable=False,
        default=False
    )

