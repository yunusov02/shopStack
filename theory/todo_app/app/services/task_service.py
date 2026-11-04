from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.core.exceptions import TaskNotFoundError
from app.db.models import TaskORM
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreateSchema, TaskUpdateSchema


class TaskService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = TaskRepository(db)

    def list_tasks(self) -> Sequence[TaskORM]:
        return self.repo.list()

    def create_task(self, payload: TaskCreateSchema) -> TaskORM:
        task = TaskORM(title=payload.title, completed=False)
        self.repo.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update_task(self, task_id: str, payload: TaskUpdateSchema) -> TaskORM:
        task = self._get_or_raise(task_id)

        if payload.title is not None:
            task.title = payload.title
        if payload.completed is not None:
            task.completed = payload.completed

        self.db.commit()
        self.db.refresh(task)
        return task

    def delete_task(self, task_id: str) -> None:
        task = self._get_or_raise(task_id)
        self.repo.delete(task)
        self.db.commit()

    def _get_or_raise(self, task_id: str) -> TaskORM:
        task = self.repo.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task
