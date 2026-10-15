from uuid import uuid4, UUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import TimeStampMixin



class TestModel(TimeStampMixin):

    __tablename__ = "test"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(50))



