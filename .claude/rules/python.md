---
paths:
  - "**/*.py"
---

# Python code standards

## Module structure
`src/` is a flat source root (no named package): `src/core/` for shared code, `src/modules/<module>/` for domain modules, imported as `from core...` and `from modules...`. See `docs/project-structure.md`. Each domain module lives in `src/modules/<module>/` and consists of:
- `router.py`: HTTP layer only (request handling, DI, status codes). No business logic, no SQL.
- `schemas.py`: Pydantic models for input and output. SQLAlchemy models are never returned from the API directly.
- `service.py`: business logic and the transaction boundary (Unit of Work). Knows nothing about HTTP: raises domain exceptions instead of `HTTPException`.
- `repository.py`: DB queries only. Never commits; committing is the UoW's job.
- `models.py`: SQLAlchemy 2.0 models (`Mapped[...]`, `mapped_column`).

A module never reaches into another module's `repository` or `models` directly; it goes through that module's service interface. `import-linter` enforces this from stage 13, but build the habit now.

## Async
- No blocking calls inside `async def`: `time.sleep`, `requests`, sync file or network I/O, heavy CPU work (e.g. Argon2 hashing). Use `asyncio.to_thread` or an async library instead.
- One `AsyncSession` per request or per UoW. Never share a session across tasks, and never use a global session.
- Don't rely on lazy loading: load relationships with `selectinload` or `joinedload`. Prefer `lazy="raise"` on relationships.
- Keep a reference to any background task started with `asyncio.create_task`, otherwise the GC may collect it.

## Typing and quality
- Full type hints; `mypy --strict` must pass. `Any` and `# type: ignore` only with a comment explaining why.
- `ruff check` and `ruff format` must be clean.
- No `print`; use `logging` (structlog later).
- Settings are read only through Pydantic Settings, not via `os.getenv` scattered across the code. No secrets in code or in git; examples go in `.env.example`.
- Never swallow exceptions silently (`except Exception: pass` is forbidden).

## DB and migrations
- Every model change comes with an Alembic migration. Review autogenerate output by hand; indexes, constraints, and `server_default` are often wrong.
- `downgrade()` must work too.
- Constraints live in the database: `NOT NULL`, `UNIQUE`, `CHECK`, FKs. Pydantic validation alone is not enough.
- Raw SQL uses bound parameters only (`text(...)` + bind params), never f-strings.

## Tests
- `pytest` in async mode against real Postgres (Testcontainers). Never substitute SQLite: RLS, `FOR UPDATE`, `pg_trgm`, and other features exist only in Postgres.
- Test behavior, not implementation. Every bug fix comes with a regression test.
- Tests are independent: each runs in its own transaction or on a clean database.
- Code that promises concurrency safety (locks, limits) is proven with a parallel test.
