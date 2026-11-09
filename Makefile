.PHONY: up down dev lint format typecheck test migrate revision

up:
# 	uvicorn src.main:app --reload --port 8000
	docker compose up -d

down:
# 	pkill -f "src.main:app"
	docker compose down

lint:
	uv run ruff check src/

format:
	uv run ruff format src/

typecheck:
	uv run mypy src/


dev:
	uv run uvicorn src.main:app --reload --port 8000


test:
	uv run pytest

migrate:
	uv run alembic upgrade head

revision:
	uv run alembic revision --autogenerate -m "$(m)"

