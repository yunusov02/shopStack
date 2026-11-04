from fastapi import FastAPI

app = FastAPI()


@app.get("/healthy")
def healthy() -> str:
    return "Healthy"
