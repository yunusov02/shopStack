from contextlib import asynccontextmanager

from fastapi import FastAPI




@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Start and stop the application lifespan context. 
    This function can be used to perform any setup or teardown tasks 
    when the application starts or stops.
    """

    print("Starting application lifespan...")

    yield

    print("Stopping application lifespan...")

def create_app() -> FastAPI:
    """
    Application Factory function to create and configure the FastAPI application instance.
    """

    app = FastAPI(
        title="ShopStack ERP",
        description="ShopStack ERP application",
        version="1.0.0",
        lifespan=lifespan
    )   

    # include routers middleares and other configurations
    
    return app


app = create_app()



@app.get("/health")
async def health_check():
    return {"status": "healthy"}




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, 
        host="localhost",
        port=8000,
    )

