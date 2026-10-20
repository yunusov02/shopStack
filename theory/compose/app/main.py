import os
import asyncpg
import redis.asyncio as redis
from fastapi import FastAPI

app = FastAPI()

DATABASE_URL = os.environ["DATABASE_URL"]
r = redis.from_url(os.environ["REDIS_URL"])

@app.get("/")
async def root():
    visits = await r.incr("visits")
    conn = await asyncpg.connect(DATABASE_URL)
    version = await conn.fetchval("SELECT version()")
    await conn.close()
    return {"visits": visits, "postgres": version}