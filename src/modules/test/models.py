from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import SoftDeleteMixin


class TestModel(SoftDeleteMixin):
    __tablename__ = "test_model"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
