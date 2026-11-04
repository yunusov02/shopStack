import uuid

from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class TaskORM(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str]
    completed: Mapped[bool] = mapped_column(default=False)
