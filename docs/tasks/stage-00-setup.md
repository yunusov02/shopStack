# Stage 0: Setup

Prerequisites: none. Done when `make up` brings the project up and CI is green.

## Repo and tooling `[CORE]`

- [x] **S0.T01** Create the repo, protect `main`, enable conventional commits
  Must know: git branching, branch protection, Conventional Commits

- [x] **S0.T02** `uv init`, `pyproject.toml`, lock file, `.python-version`
  Must know: uv, pyproject, lock files

- [x] **S0.T03** Configure ruff (lint + format) and mypy strict in `pyproject.toml`; fix every current error
  Must know: ruff rules, mypy strict mode, type hints

- [x] **S0.T04** Add pre-commit with ruff, ruff-format, mypy hooks; `pre-commit install`
  Must know: pre-commit, git hooks

- [x] **S0.T05** Add `Makefile`: `up`, `down`, `lint`, `format`, `typecheck`, `test`, `migrate`, `revision`
  Must know: Makefile targets, `.PHONY`

## Configuration `[CORE]`

- [ ] **S0.T06** `Settings` with pydantic-settings: DB, Redis, `DEBUG`, `ENV`; loaded from `.env`; `.env.example` in git
  Must know: pydantic-settings, environment variables, 12-factor config

- [ ] **S0.T07** Enforce UTC: a `utcnow()` helper, ruff `DTZ` rule on, a test that a naive datetime is rejected by the DB layer
  Must know: timezone-aware datetime, `datetime.now(UTC)`, timestamptz

## Database layer `[CORE]`

- [ ] **S0.T08** Async engine and `async_sessionmaker` with asyncpg
  Must know: SQLAlchemy 2.0 async, asyncpg, connection pool

- [ ] **S0.T09** Alembic with async `env.py`, first migration
  Must know: Alembic, autogenerate, async migrations

- [ ] **S0.T10** `UnitOfWork`: `__aenter__`/`__aexit__`, commit on success, rollback on error
  Must know: async context manager, transaction, AsyncSession

- [ ] **S0.T11** Declarative `Base` with naming conventions for constraints and indexes; `TimestampMixin` (`created_at`, `updated_at`, timestamptz, server default)
  Must know: SQLAlchemy declarative base, `MetaData(naming_convention=...)`, mixins

- [ ] **S0.T12** Generic `Repository[Model]` base: `get`, `add`, `list` with typed generics; `BaseService` holding the UoW
  Must know: Python generics, `TypeVar`, repository pattern, service layer

## Application `[CORE]`

- [ ] **S0.T13** Modular layout: `src/modules/<name>/{router,schemas,service,repository,models}.py`; `src/core/` for shared code; delete `app/models/test.py`
  Must know: Python packages, import paths, modular monolith

- [ ] **S0.T14** App factory `create_app()` and lifespan: engine and sessionmaker created on startup, stored on `app.state`, disposed on shutdown; no DB access at import time; `logging` instead of `print`
  Must know: FastAPI lifespan, `app.state`, `AsyncEngine.dispose()`, `asynccontextmanager`

- [ ] **S0.T15** `get_session` / `get_uow` dependencies reading from `app.state`
  Must know: FastAPI `Depends`, generator dependencies

- [ ] **S0.T16** Middleware order and request lifecycle: correlation ID middleware (`X-Request-ID`), CORS with explicit origins from settings, global exception handler with one error format `{code, message, details}`
  Must know: ASGI middleware, CORS, FastAPI exception handlers

- [ ] **S0.T17** `/health/live` (always 200) and `/health/ready` (checks DB and Redis with a timeout)
  Must know: liveness vs readiness, `SELECT 1`, asyncio timeout

## Tests `[CORE]`

- [ ] **S0.T18** pytest config: `asyncio_mode = auto`, `tests/` layout (`unit/`, `integration/`), `tests/README.md` describing the pyramid
  Must know: pytest, pytest-asyncio, test pyramid

- [ ] **S0.T19** Testcontainers fixture: Postgres container per session, migrations applied once, transaction rollback per test
  Must know: Testcontainers, session vs function fixture scope, nested transactions / savepoints

- [ ] **S0.T20** httpx client fixture with `ASGITransport` and lifespan; `dependency_overrides` example for settings
  Must know: httpx `ASGITransport`, `app.dependency_overrides`

- [ ] **S0.T21** Tests: health endpoints, UoW commit/rollback, error format
  Must know: pytest-asyncio, assertions on JSON responses

## Docker `[CORE]`

- [ ] **S0.T22** `docker-compose.yaml`: Postgres and Redis with healthchecks and volumes; host ports different from local 5432/6379
  Must know: Docker Compose, healthcheck, volumes, port mapping

- [ ] **S0.T23** Multi-stage `Dockerfile`: builder (uv sync, no dev deps) → slim runtime, non-root user, `uvicorn` entrypoint
  Must know: Docker multi-stage build, image layers, uv in Docker

- [ ] **S0.T24** `app` service in Compose with `depends_on: condition: service_healthy`, env from `.env`; `make up` works from a clean clone
  Must know: Compose service dependencies, env files

## CI `[CORE]`

- [ ] **S0.T25** GitHub Actions: ruff, mypy, pytest (Testcontainers in CI), on PR and on `main`
  Must know: GitHub Actions, services/Docker in CI, caching uv

- [ ] **S0.T26** CI job: `alembic upgrade head` on an empty DB, then `alembic check` (no pending autogenerate diff)
  Must know: Alembic `check`, migration drift

- [ ] **S0.T27** CI job: build the Docker image, tag with the commit SHA (the build artifact)
  Must know: `docker build` in CI, image tags

## ADRs `[CORE]`

- [ ] **S0.T28** ADR 0001: modular monolith
  Must know: ADR template (roadmap), monolith vs microservices trade-offs

- [ ] **S0.T29** ADR 0002: FastAPI for the monolith, Django for the Platform service
  Must know: FastAPI vs Django strengths

- [ ] **S0.T30** ADR 0003: async vs sync, ASGI vs WSGI
  Must know: event loop, I/O-bound vs CPU-bound, ASGI/WSGI

- [ ] **S0.T31** ADR 0004: repository and Unit of Work
  Must know: repository pattern, Unit of Work, what they cost

- [ ] **S0.T32** ADR 0005: frontend (back-office Jinja2 + HTMX, POS as a PWA later)
  Must know: server-rendered UI vs SPA, HTMX basics
