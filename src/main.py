from sqlalchemy import text

from src.app import create_app

app = create_app()


@app.get("/health")
async def health() -> dict[str, str]:

    async with app.state.engine.connect() as conn:
        res = await conn.execute(text("SELECT 1"))
        value = res.scalar_one_or_none()

        if value != 1:
            return {"status": "error", "message": "Database connection failed"}

        return {"status": "ok"}

    return {"status": "error"}
