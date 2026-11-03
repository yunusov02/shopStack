# Project structure (final state)

This document shows the folder layout of the shopStack monorepo as it will look after stage 41 of `docs/retail-saas-roadmap.md`. It is derived from the roadmap's "Where:" lines, the architecture diagram, the service catalog and the task files in `docs/tasks/`.

The tree grows stage by stage. At stage 0 only the root files, `src/core/`, `src/app.py`, `migrations/`, `tests/` and `.github/workflows/ci-core.yml` exist. Everything else appears when its stage starts.

Layout decision: `src/` is a flat source root, not a named package. Code is imported as `from core.db import Base` and `from modules.catalog.service import CatalogService`. `src` is put on the import path (`pythonpath = ["src"]` in pytest, `PYTHONPATH=/app/src` in the Docker image). The app is not built as a wheel; the Docker image copies `src/` directly.

## Tree

```
shopStack/
├── .github/
│   ├── workflows/
│   │   ├── ci-core.yml              # ruff, mypy, pytest, alembic check, image build (S0.T25–27)
│   │   ├── ci-services.yml          # matrix: only changed services (stages 13, 21)
│   │   ├── ci-data.yml              # dbt slim CI, contract compatibility (stages 35, 37)
│   │   ├── ci-ml.yml                # feature transform tests, golden sets (stages 38, 41)
│   │   └── cd.yml                   # staging → approval → production (stage 21)
│   ├── CODEOWNERS                   # one owner per schema (S37 [EXT])
│   └── PULL_REQUEST_TEMPLATE.md     # happy path, edge cases, fallback, blast radius
│
├── .claude/                         # rules/, skills/
├── .pre-commit-config.yaml
├── .python-version
├── .env.example
├── pyproject.toml                   # uv workspace root + core monolith
├── uv.lock                          # one lock file for the whole workspace
├── Makefile                         # up, down, lint, format, typecheck, test, migrate, revision, seed, lake-up ...
├── Dockerfile                       # core image (multi-stage, non-root)
├── docker-compose.yaml              # Postgres, Redis, app (stage 0); extended with profiles later
├── alembic.ini
├── README.md                        # benchmark results live here ("break it and measure")
├── CLAUDE.md
│
├── src/                             # ─── CORE: FastAPI modular monolith (flat source root) ───
│   ├── app.py                       # create_app(), lifespan, middleware order
│   ├── cli.py                       # typer: create_tenant, replay_dlq, seed (S1.T48)
│   ├── core/                        # the only shared layer modules may import (import-linter)
│   │   ├── __init__.py
│   │   ├── config.py                # pydantic-settings
│   │   ├── time.py                  # utcnow()
│   │   ├── errors.py                # domain exceptions + {code, message, details}
│   │   ├── db/                      # engine, session, Base, naming conventions, mixins, UoW
│   │   ├── repository.py            # Repository[Model], BaseService
│   │   ├── tenancy/                 # contextvars, middleware, TenantMixin, global filter, RLS SET LOCAL
│   │   ├── security/                # jwt, argon2, csrf, security headers, outbound URL validator (SSRF)
│   │   ├── permissions.py           # permission codes + require_permission()
│   │   ├── cache.py                 # Redis cache-aside, tenant prefix, distributed lock
│   │   ├── rate_limit.py
│   │   ├── idempotency.py           # Idempotency-Key store
│   │   ├── audit.py                 # audit() helper → outbox → Audit service
│   │   ├── events/                  # envelope, outbox model, relay (SKIP LOCKED), inbox
│   │   ├── state_machine.py         # generic transition() (moves to modules/workflow in stage 30)
│   │   ├── money.py                 # Money value object, largest-remainder allocation
│   │   └── observability/           # structlog, correlation id, OpenTelemetry, Prometheus
│   │
│   ├── modules/                     # each: router / schemas / service / repository / models
│   │   ├── __init__.py              # plus tasks.py (Celery) and events.py (domain events) when needed
│   │   ├── accounts/                # User, Membership, auth, OTP, TOTP, sessions, Role, invites
│   │   ├── tenants/                 # Tenant, Domain, Location, TenantSettings (replica from stage 15)
│   │   ├── catalog/                 # stage 2
│   │   ├── inventory/               # stage 3 (+ stage 33 intercompany)
│   │   ├── procurement/             # stage 4
│   │   ├── sales/                   # stage 5: cart, payment, receipt, shift, step-up approval
│   │   ├── pricing/                 # stage 6: engine.py is a pure function
│   │   ├── customers/               # stage 7: loyalty, credit and store-credit ledgers
│   │   ├── finance/                 # stage 8
│   │   ├── hr/                      # stages 11, 31
│   │   ├── sync/                    # stage 12: offline POS sync protocol
│   │   ├── orders/                  # stage 17: storefront API, order state machine
│   │   ├── integrations/            # stage 19: ports/ (interfaces), adapters/, fakes/, webhooks
│   │   ├── accounting/              # stages 26, 33: GL, posting engine (pure), periods
│   │   ├── credit/                  # stage 27: installments, gift cards
│   │   ├── production/              # stage 28: BOM, work orders, WIP
│   │   ├── planning/                # stage 29: forecast baseline, replenishment
│   │   ├── workflow/                # stage 30: state machine framework, approvals, numbering
│   │   ├── payroll/                 # stage 31
│   │   ├── reporting/               # stage 32: report engine, exports, i18n
│   │   ├── documents/               # stage 32: templates, PDF worker
│   │   └── experiments/             # stage 40: A/B assignment, exposure events
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1.py                    # aggregates /api/v1 routers
│   │   ├── storefront.py            # /api/storefront/v1 (public, tenant resolved by domain)
│   │   └── internal.py              # commands from services (service token); never exposed via ingress
│   ├── web/                         # back-office: Jinja2 + HTMX
│   │   ├── templates/
│   │   ├── static/
│   │   └── routes/
│   ├── consumers/                   # Kafka consumers: tenant.*, delivery.*, forecast.published ...
│   └── worker/
│       ├── __init__.py
│       ├── celery_app.py            # S9.T01
│       ├── beat.py                  # schedules
│       └── session.py               # sync SQLAlchemy session for workers
│
├── migrations/                      # core Alembic
│   ├── env.py
│   └── versions/
│
├── tests/                           # core tests
│   ├── README.md                    # test pyramid (S0.T18)
│   ├── conftest.py                  # Testcontainers, httpx ASGITransport, two-tenant fixtures
│   ├── unit/                        # pure engines: pricing, posting, payroll, hypothesis
│   ├── integration/                 # real Postgres: RLS, locks, parallel tests
│   ├── e2e/                         # Playwright (stage 18)
│   ├── contracts/                   # Pact (stages 16, 18, 24)
│   └── load/                        # Locust: 50 cashiers (stage 5)
│
├── services/                        # ─── each one is its own deploy unit: pyproject, Dockerfile, database ───
│   ├── notification/                # stage 14: FastAPI + RabbitMQ worker
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   ├── migrations/
│   │   ├── src/                     # app.py, worker.py, channels/ (sms, telegram, email adapters), templates/
│   │   └── tests/
│   ├── platform/                    # stage 15: Django + DRF + Celery
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   ├── manage.py
│   │   ├── config/settings/{base,dev,test,prod}.py
│   │   ├── apps/                    # tenants, billing, staff, provisioning (saga); each with services.py
│   │   └── tests/
│   ├── analytics/                   # stage 16: FastAPI, Kafka projections, ClickHouse [OPT]
│   ├── delivery/                    # stage 18: FastAPI, PostGIS, Redis GEO, WebSocket
│   ├── audit/                       # stage 22: Django + DRF, RunSQL migrations, hash chain
│   ├── media/                       # stage 23: FastAPI + image worker, MinIO
│   ├── supplier-portal/             # stage 24: Django + DRF + HTMX, custom user model
│   ├── marketplace-sync/            # stage 25: FastAPI + worker, fake marketplace server
│   ├── ml-serving/                  # stages 39–40: FastAPI, MLflow registry, predict API
│   └── assistant/                   # stage 41: FastAPI, RAG, text-to-SQL, agents, SSE
│
├── pos-terminal/                    # stage 12: React + TypeScript PWA, IndexedDB, client outbox
├── courier-app/                     # stage 18: courier PWA
│
├── data/                            # ─── DATA PLATFORM (stages 34–37) ───
│   ├── README.md                    # layer contract: bronze / silver / gold
│   ├── pyproject.toml
│   ├── ingestion/                   # events→bronze consumer, debezium/ connector configs, backfill
│   ├── lake/                        # Iceberg catalog config, table schemas, compaction
│   ├── dags/                        # Airflow DAGs (no business logic; import from data/)
│   ├── warehouse/                   # dbt project
│   │   ├── dbt_project.yml
│   │   ├── models/{staging,intermediate,marts}/
│   │   ├── snapshots/               # SCD Type 2
│   │   ├── seeds/                   # dim_date, Uzbekistan holidays
│   │   ├── tests/                   # singular: debit = credit, no negative stock
│   │   └── macros/
│   ├── jobs/                        # PySpark: batch/ (shuffle, skew lab), streaming/ (watermarks)
│   ├── quality/                     # Great Expectations suites, quality gates, quarantine
│   ├── contracts/                   # one schema per consumed event and CDC table; CI compatibility
│   └── tests/
│
├── ml/                              # ─── ML PLATFORM (stages 38–41) ───
│   ├── pyproject.toml               # heavy deps (lightgbm, mlflow, torch [OPT]) live only here
│   ├── features/                    # versioned transforms; the same code for training and serving
│   ├── pipelines/                   # <problem>/train.py + config.yaml, run from Airflow
│   │   ├── forecast/
│   │   ├── churn/
│   │   ├── segmentation/
│   │   ├── recsys/
│   │   └── anomaly/
│   ├── models/                      # recsys/, anomaly/, embeddings/ (model code, baselines)
│   ├── llm/                         # provider adapters, prompts/ (versioned files), eval/ golden sets
│   └── tests/
│
├── notebooks/                       # exploration only; a notebook used twice becomes a module
│
├── deploy/
│   ├── compose/                     # kafka.yaml, observability.yaml, data.yaml, ml.yaml (profiles / overrides)
│   ├── helm/
│   │   ├── library/                 # shared library chart
│   │   ├── charts/<service>/        # one chart per service
│   │   └── shopstack/               # umbrella chart
│   ├── k8s/                         # k3d config, network policies, KEDA scalers
│   ├── terraform/                   # [EXT] Infrastructure as Code
│   └── observability/               # grafana/dashboards, prometheus/rules, alerts, otel-collector, loki
│
├── scripts/                         # seed_10m.py, replay_dlq.py, verify_chain.py, backup_restore.sh
│
└── docs/
    ├── retail-saas-roadmap.md
    ├── project-structure.md         # this file
    ├── tasks/
    ├── adr/                         # 0001-modular-monolith.md ... 0081-agent-tools.md
    ├── rfc/                         # 0001-kafka-vs-rabbitmq.md
    ├── postmortems/
    ├── runbooks/                    # data-platform.md, consumer-lag.md ...
    ├── notes/                       # ml.md (leakage checklist), stats.md, llm.md, cloud-mapping.md
    └── model-cards/                 # stage 39, generated from the registry
```

## Key decisions and why

- **One monorepo, but every service is its own deploy unit.** The root `pyproject.toml` is a uv workspace whose members are `services/*`, `data` and `ml`. A single `uv.lock` prevents version conflicts across packages. Each service still has its own `Dockerfile` and its own database, because the roadmap requires that no service writes to another service's database. Alternative: a polyrepo. Cost of the polyrepo: ten or more repositories whose contract tests and CI must be kept in sync by hand. Cost of the monorepo: CI needs logic to build and deploy only the services that changed (stages 13 and 21 teach exactly that).
- **Flat `src/` source root, no named package.** Imports are short (`from core.db import Base`) and match S0.T13 in `docs/tasks/stage-00-setup.md`. The cost: `src` must be on the import path explicitly (pytest `pythonpath`, `PYTHONPATH` in Docker), the app cannot be built as a wheel, and the top-level names `core`, `modules`, `api` are generic. Each service has its own `src/` with its own working directory and image, so the names do not collide at runtime; inside one process only one `src/` is ever on the path. Alternative: `src/shopstack/` (src layout with a package), which allows a wheel and fully qualified names at the cost of longer imports and a build-system section in `pyproject.toml`. Rejected to keep stage 0 simple; revisit in an ADR if the wheel build becomes necessary.
- **`core/` is the single shared layer for modules.** From stage 13 `import-linter` enforces the rule that `modules/*` may import only `core` and other modules' service interfaces. This is what makes a later extraction into a service possible.
- **`data/` and `ml/` live outside the core with their own `pyproject.toml`.** Heavy dependencies (Spark, LightGBM, torch) never enter the core image. The part III rule applies: the platform never writes to the core database; results come back as events or as commands to the internal API.
- **`deploy/` is separate, the root `docker-compose.yaml` stays.** S0.T22 requires a root compose file. Kafka, observability and the lake get override files under `deploy/compose/`, otherwise one compose file with forty services becomes unreadable.

## Current repo state to clean up

- The root `main.py` and the `theory/` folder are not part of this structure. `theory/` should move to its own repository or be excluded from ruff and mypy, otherwise it turns CI red.
- `pyproject.toml` pins `requires-python >= 3.14` while the roadmap says 3.13+. This is fine as long as the Docker base image and the CI matrix use the same version.
