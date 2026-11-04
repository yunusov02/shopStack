from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import TaskORM


class TaskRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> Sequence[TaskORM]:
        return self.db.scalars(select(TaskORM)).all()

    def get(self, task_id: str) -> TaskORM | None:
        return self.db.get(TaskORM, task_id)

    def add(self, task: TaskORM) -> None:
        self.db.add(task)

    def delete(self, task: TaskORM) -> None:
        self.db.delete(task)
