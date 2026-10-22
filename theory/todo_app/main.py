from fastapi import FastAPI

app = FastAPI()



@app.get("/")
async def read_base_page():
    return "Hello World"




