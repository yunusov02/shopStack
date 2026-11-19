from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from shopstack.core.routers import  router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:

    print("Starting lifespan")

    yield


    print("Stopping lifespan")


def create_app() -> FastAPI:

    application = FastAPI(lifespan=lifespan)
    application.include_router(router)
    return application


app = create_app()



@app.get("/")
async def root():
    return {"message": "Hello World"}

