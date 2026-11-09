from fastapi import APIRouter

api_router = APIRouter(
    prefix="/api",
    tags=["api"],
)


# api_router.include_router()
