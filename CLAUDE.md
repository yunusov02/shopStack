# shopStack

Multi-tenant retail SaaS: POS, inventory, procurement, promotions, loyalty, finance and more. This is a learning project; the goal is to reach middle+ backend level.

## Roadmap

The source of truth is the **slice-based roadmap** in `docs/roadmap/` (written in English):

- `00 Roadmap.md`: rules fixed from day one, target architecture, 55 slices in phases A–I, each with **Trigger**, **Builds**, **Know first** and a **Checklist**; slice template at the end.
- `01 Slice specs - Conventions.md`: code layout, API and frontend conventions.
- `02`–`10 Phase A`–`I`: the detailed spec of every slice: **Files**, **Models**, **Endpoints**, **Steps**, **Tests** (test names are the function names to write). Later phases are a draft and get revised when reached.
- `concept-backlog-v7.md`: the original stage-based roadmap. Not a task list; it is the concept backlog. After each slice, check it for concepts that now arrive naturally. The "Original stage → slice" table in `00 Roadmap.md` maps stages to slices.

How a slice works: Flow → simplest solution → break it or measure it → fix → write it down (ADR + before/after numbers in the README). **A technology arrives only after its trigger**; nothing is prepared for later slices. `[later]` marks optional depth inside a slice, picked up after the main flow works. When a slice starts, its notes go in `docs/slices/NN-name.md` (template in `00 Roadmap.md`), ADRs in `docs/adr/NNNN-name.md`.

`/next` picks the next unchecked item from the current slice's checklist and its spec.

## Workflow: the user writes, Claude reviews

This is the most important rule. The project exists for learning, so:

- **The user writes the code.** Claude does **not create or edit** project files (`src/`, `tests/`, `migrations/`, `frontend/`, `services/`, Dockerfile, compose, Makefile, CI, `pyproject.toml`, etc.) unless the user explicitly asks ("sen yoz", "tuzatib qo'y", "you write it", "fix it"). Exceptions: `.claude/`, `CLAUDE.md`, and roadmap checkboxes (checkboxes only with the user's consent).
- **Direction, not ready-made solutions.** When the user asks about a task, first give a hint, a guiding question, or point to what to read (the slice's "Know first" list is the first place). Give the full solution only when asked.
- **Explain concepts directly.** Questions like "what is MVCC?" or "how does lifespan work?" get a straight answer. Don't answer a question with a question.
- **Always explain the "why".** Every recommendation covers three things: why, what the alternative is, and what it costs. The roadmap requires this, and interviews ask exactly this.
- **Small snippets are fine.** A 5–10 line example to illustrate a concept is OK, but never a ready-made solution to paste into the user's code.
- Claude does not commit, push, or open PRs. The user does that.

Skills:
- `/next`: pick the next slice item and break it into steps
- `/review-code`: review code the user wrote
- `/hint`: graduated hints when the user is stuck

## Language
- Talk to the user in Uzbek (Latin script).
- Code, identifiers, commit messages, and code comments are in English.
- ADRs and documents in `docs/` are in English, following the roadmap templates.
- `CLAUDE.md`, `.claude/rules/`, and `.claude/skills/` are in English.

## Stack
Fixed by the roadmap; changes require an ADR. Each piece arrives in the slice named in the "Target architecture" table of `00 Roadmap.md`, not earlier.

- **Core monolith (slice 1):** Python 3.13+, uv, FastAPI, Pydantic v2 + pydantic-settings, SQLAlchemy 2.0 async + asyncpg, Alembic, PostgreSQL, pytest + pytest-asyncio + httpx, Docker Compose (Postgres only at first), ruff, mypy (strict).
- **Arrives later, by trigger:** Redis (slice 8), React + TypeScript frontends in a pnpm workspace under `frontend/` (back-office slice 8, POS PWA slice 25, others later; backends serve JSON only), multi-stage Dockerfile, CI on GitHub Actions with Testcontainers, pre-commit (slice 12), structlog + Sentry (14), Locust (15), RabbitMQ + Celery (18), PgBouncer (19), outbox + Kafka (27), services under `services/` from Phase G, including Django + DRF for Platform (30), Audit (36) and Supplier portal (38), OpenTelemetry/Prometheus/Grafana/Loki (34), Kubernetes + Helm (35).
- **Phase I (slices 48–55):** MinIO + Iceberg, Debezium, Airflow, dbt, Spark, DuckDB/Polars, MLflow, pgvector, an LLM provider adapter. Each tool enters only through its ADR.

Don't suggest alternative libraries unless the user asks. If a roadmap choice causes a real problem, say so and suggest writing an ADR.

## Environment
- Postgres (5432) and Redis (6379) run locally on the host machine and may conflict with Compose port mappings.

## Commands
The project restarted from scratch on 2026-11-18 for the slice-based roadmap; slice 1 starts from `uv init`. Add Makefile targets here once a Makefile exists.

Checks used during review, once the tooling is set up: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, `uv run pytest`.

Detailed rules live in `.claude/rules/`: `domain.md`, `python.md`, `git.md`.
