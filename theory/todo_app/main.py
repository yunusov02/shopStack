import uuid

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http:localhost:3000"],
    allow_methods=["*"]
)




class TaskSchema(BaseModel):
    id: str
    title: str
    completed: bool


class TaskCreateSchema(BaseModel):
    title: str


class TaskUpdateSchema(BaseModel):
    title: str | None = None
    completed: bool | None = None


tasks: list[TaskSchema] = []


@app.get("/")
async def read_base_page():
    return "Hello World"


@app.get("/tasks")
async def get_tasks() -> list[TaskSchema]:
    return tasks


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreateSchema) -> TaskSchema:
    
    new_task = TaskSchema(
        id=str(uuid.uuid4()),
        title=payload.title,
        completed=False
    )
    
    tasks.append(new_task)
    
    return new_task

@app.patch("/tasks/{task_id}")
async def update_task(task_id: str, payload: TaskUpdateSchema) -> TaskSchema | str:
    
    for task in tasks:
        if task.id == task_id:
            
            task.title = payload.title if payload.title else task.title
            task.completed = payload.completed if payload.completed else task.completed
            
            return task
        
        
    return "Task Not Found"
    


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str):
    
    for task in tasks:
        
        if task.id == task_id:
            tasks.remove(task)
