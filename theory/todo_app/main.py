import uuid

from fastapi import FastAPI
from pydantic import BaseModel



class TaskSchema(BaseModel):
    id: str
    title: str
    completed: bool


class TaskCreateSchema(BaseModel):
    title: str

app = FastAPI()


tasks: list[TaskSchema] = []


@app.get("/")
async def read_base_page():
    return "Hello World"


@app.get("/tasks")
async def get_tasks() -> list[TaskSchema]:
    return tasks


@app.post("/tasks")
async def create_task(payload: TaskCreateSchema) -> TaskSchema:
    
    new_task = TaskSchema(
        id=str(uuid.uuid4()),
        title=payload.title,
        completed=False
    )
    
    tasks.append(new_task)
    
    return new_task

