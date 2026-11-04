from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import TaskNotFoundError
from app.db.database import get_db
from app.db.models import TaskORM
from app.schemas.task import TaskCreateSchema, TaskSchema, TaskUpdateSchema
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(db: Annotated[Session, Depends(get_db)]) -> TaskService:
    return TaskService(db)


ServiceDep = Annotated[TaskService, Depends(get_task_service)]


# Sync `def` on purpose: the DB driver is sync, so FastAPI runs these in a threadpool
# instead of blocking the event loop.
@router.get("", response_model=list[TaskSchema])
def get_tasks(service: ServiceDep) -> Sequence[TaskORM]:
    return service.list_tasks()


@router.post("", response_model=TaskSchema, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreateSchema, service: ServiceDep) -> TaskORM:
    return service.create_task(payload)


@router.patch("/{task_id}", response_model=TaskSchema)
def update_task(task_id: str, payload: TaskUpdateSchema, service: ServiceDep) -> TaskORM:
    try:
        return service.update_task(task_id, payload)
    except TaskNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, service: ServiceDep) -> None:
    try:
        service.delete_task(task_id)
    except TaskNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e)) from e
