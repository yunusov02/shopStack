# Retail SaaS Platform: Middle+ Engineer Roadmap (v6: FastAPI + Django)

Multi-tenant SaaS: **POS + inventory + procurement + pricing and promotions + customers and loyalty + finance + analytics + offline POS + e-commerce + delivery + integrations**.

**Part II (ERP extension, stages 26–33):** general ledger and accounting, installment sales and gift cards, production, demand planning, workflow engine, payroll, reporting and documents, multi-company.

Goal: learn middle+ backend concepts in practice through one project, and understand **why** every technical decision was made.

---

## How to use

- **No deadlines.** A stage is finished only when its **"Done when"** criterion is met.
- **"Prerequisites"** define the order of stages.
- Every task is tagged:

| Tag | Meaning |
|---|---|
| `[CORE]` | Required. Teaches an important new concept, or later stages depend on it |
| `[EXT]` | Extension. Done after the core, adds extra depth |
| `[OPT]` | Optional. If you have time or the topic interests you |

> **Scope rule:** this list is the size of a full commercial ERP. In real companies, teams build this over years. First finish the `[CORE]` part of every stage, then come back to `[EXT]` and `[OPT]`. 40 finished features are worth far more than 100 unfinished ones.

### MVP line

| Level | Stages (`[CORE]` part) | Result |
|---|---|---|
| 1. Job-ready | 0, 1, 2, 3, 5, 9, 10 | A working multi-tenant POS, concurrency, performance. **Start applying for jobs** |
| 2. Strong domain | 4, 6, 7, 8 | Procurement, promotions engine, loyalty, finance |
| 3. Close to senior | 12, 13, 14, 16 | Offline sync, events, first services |
| 4. Full platform | 11, 15, 17–21 | HR, Platform and Billing (Django), e-commerce, delivery, integrations, K8s |
| 5. Additional services | 22–25 | Audit and Supplier portal (Django + DRF), Media and Marketplace sync (FastAPI) |
| 6. ERP | 26–33 (part II) | General ledger, installments, production, planning, workflow engine, payroll, reporting, multi-company. The project becomes a full ERP |

> **About level 5:** these stages were added to the roadmap later; their numbers reflect the order they were added, not the order of work. Work order follows **"Prerequisites"**: stage 23 can start after stage 14, stages 22 and 24 after you have Django experience, i.e. after stage 15. But finish the `[CORE]` part of levels 1–3 first: every new service is a permanent cost (CI, database, monitoring, contract tests).

> **About level 6 (part II):** these stages turn the retail SaaS into an ERP. None of them is needed for a job search; all of them are what separates "built a shop app" from "built an ERP" in an interview. They live in the monolith and reuse the ledgers, state machines and approval flows of part I. See **Part II** after stage 25.

> **Concept index:** every interview term (database, distributed systems, API, caching, messaging, architecture, Python, Django, testing, observability, DevOps, security, performance, team vocabulary) is mapped to the stage or theory track where this roadmap teaches it. See **Concept index** near the end.

---

## General rules

### Engineering rules (every stage)
- [ ] Every stage ends in a working, tested, deployable state
- [ ] Tests are written together with the code, CI is always green
- [ ] An ADR for every important decision (`docs/adr/`)
- [ ] **"Break it and measure":** measure before and after every optimization, record the results in the README
- [ ] For every technology, have an answer ready: why this one, what the alternative is, what it costs

### Domain rules (whole project)
- [ ] **Money is `Decimal` only**, or an integer amount in tiyin. Never `float`
- [ ] **Stock decrements are never asynchronous.** A sale and its stock change happen in one ACID transaction
- [ ] **Documents are not edited, they are corrected.** A completed sale, receipt or transfer is never changed; a mistake is fixed with a new document (return, adjustment, reversal/storno)
- [ ] **Snapshots:** a sale line stores price, cost, tax and applied promotions as they were at that moment. Later price changes must not break old sales
- [ ] **Every balance comes from a ledger:** stock, customer balance, points, debts. Every change is an immutable entry
- [ ] **Every document has a state machine** (`draft → ... → completed/cancelled`), transitions are logged
- [ ] **Sensitive operations** (refund, void, manual discount, price change, adjustment) are protected by a permission and written to the audit log

---

## Architecture (final state)

```
  CLIENTS
  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
  │ Back-office   │  │ POS terminal  │  │ Storefront    │  │ Courier app   │  │ Suppliers     │  │ Staff         │
  │ Jinja2 + HTMX │  │ React+TS PWA  │  │ web shop      │  │ PWA           │  │ browser, ERP  │  │ platform and  │
  │               │  │ offline-first │  │               │  │               │  │ API           │  │ audit admin   │
  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘
          │                  │                  │                  │                  │                  │
          └──────────────────┴──────────────────┴─────────┬────────┴──────────────────┴──────────────────┘
                                                          │ HTTPS / WebSocket
                                                          ▼
  ┌─ EDGE ────────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ Ingress: wildcard *.<domain>, TLS (cert-manager), host-based routing, edge rate limits                        │
  │ <tenant>.<domain>, /api/storefront → monolith         suppliers.<domain>         → supplier portal            │
  │ admin.<domain>                     → platform, audit   courier.<domain>, tracking → delivery                  │
  │ media.<domain>                     → media (presign)   webhooks.<domain>          → provider callbacks        │
  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
  ┌─ CORE ───────────────────────────────────────────────────────────────────────┐    ┌─ DATA ────────────────────┐
  │ FastAPI modular monolith (SQLAlchemy 2.0 async, Pydantic v2)                 │    │ PgBouncer → PostgreSQL    │
  │ accounts · tenants (replica) · catalog · inventory · procurement             │    │ RLS, FTS, partitions      │
  │ sales · pricing · customers · finance · orders · hr · sync                   │◄──►│                           │
  │ accounting · credit · production · planning · workflow · payroll · reporting │    │                           │
  │ integrations: payment, fiscal, printer adapters · outbound webhooks          │    │ Redis                     │
  │ outbox table + relay (FOR UPDATE SKIP LOCKED)                                │    │ cache, OTP, sessions,     │
  │ internal API ◄── commands from delivery, supplier portal, marketplace sync   │    │ locks, rate limits, GEO   │
  └──────────────────────────────────────────────────────────────────────────────┘    └───────────────────────────┘
                    │ outbox relay                          │ Celery tasks and commands, after commit
                    │                                       ▼
  ASYNC             │                           ┌────────────────────────────┐
                    │                           │ RabbitMQ                   │
                    │                           │ → Celery workers + beat    │
                    │                           │ → notification commands    │────────────────────────┐
                    │                           └────────────────────────────┘                        │
                    ▼                                                                                 │
  ══════════════════════ KAFKA · domain events · partitioned by tenant_id ════════════════════════════╫════════════
               ▼                            ▼                            ▼                            ▼
  ┌─ 15 · Platform+Billing ─┐  ┌─ 16 · Analytics ────────┐  ┌─ 18 · Delivery ─────────┐  ┌─ 14 · Notification ─────┐
  │ Django + DRF, Celery    │  │ FastAPI                 │  │ FastAPI, WebSocket      │  │ worker + FastAPI        │
  │ own Postgres            │  │ Postgres, ClickHouse    │  │ PostGIS + Redis GEO     │  │ own Postgres            │
  │ tenant registry, plans, │  │ dashboards, ABC,        │  │ zones, quotes, dispatch │  │ templates, preferences, │
  │ invoices, staff admin   │  │ turnover, forecasts     │  │ live tracking, handover │  │ retries, DLQ, status    │
  │ JWKS, impersonation     │  │ read-only projections   │  │ courier cash ledger     │  │ fed by RabbitMQ         │
  └─────────────────────────┘  └─────────────────────────┘  └─────────────────────────┘  └─────────────────────────┘
  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ Kafka (same cluster) ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
               ▼                            ▼                            ▼                            ▼
  ┌─ 22 · Audit ────────────┐  ┌─ 23 · Media ────────────┐  ┌─ 24 · Supplier portal ──┐  ┌─ 25 · Marketplace sync ─┐
  │ Django + DRF            │  │ FastAPI + worker        │  │ Django + DRF + HTMX     │  │ FastAPI + worker        │
  │ own Postgres            │  │ own Postgres + MinIO    │  │ own Postgres            │  │ own Postgres + Redis    │
  │ append-only storage,    │  │ presigned uploads,      │  │ PO replica, ASN,        │  │ stock and price push,   │
  │ per-tenant hash chain   │  │ thumbnails, orphan GC   │  │ invoices, ERP API       │  │ order import, conflict  │
  │ read-only admin         │  │                         │  │ cross-tenant identity   │  │ rate limit, breaker     │
  └─────────────────────────┘  └─────────────────────────┘  └─────────────────────────┘  └─────────────────────────┘
                                                          │ through adapters: timeouts, retries, circuit breakers
                                                          ▼
  ┌─ EXTERNAL ────────────────────────────────────────────────────────────────────────────────────────────────────┐
  │ SMS gateway · Telegram · email · Payme / Click · card and QR terminals · fiscal service (check current rules) │
  │ marketplaces (e.g. Uzum Market) · tenant webhook endpoints · 1C exports · receipt printers and scales         │
  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

  ┌─ OBSERVABILITY AND RUNTIME (every service) ───────────────────────────────────────────────────────────────────┐
  │ OpenTelemetry traces · Prometheus metrics · Loki logs · Grafana dashboards and alerts · Sentry                │
  │ correlation ID across HTTP, Kafka, RabbitMQ, Celery · Kubernetes + Helm · HPA / KEDA · CD: staging → prod     │
  └───────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

How to read the diagram:
- **Clients** reach everything through one **edge** (ingress), which routes by host: tenant subdomains and the storefront go to the monolith, and each service has its own host.
- **The core** (monolith) owns everything that must be strongly consistent. It writes domain events to its **outbox** table in the same transaction, and the relay publishes them to **Kafka**.
- **RabbitMQ** carries work, not facts: Celery tasks and notification commands, sent only after commit.
- **Services** consume events from Kafka and publish their own events through their own outbox. None of them writes to another service's database.
- Delivery, Supplier portal and Marketplace sync change data in the core only by sending **commands** to its internal API (service token + `Idempotency-Key`); the core's state machines decide the outcome.
- Clients upload files directly to MinIO using presigned URLs from Media; files never pass through the core.
- Every call to the outside world goes through an **adapter** with timeouts, retries and a circuit breaker.

### What lives where

| Part | Location | Reason |
|---|---|---|
| Auth, catalog, inventory, procurement, sales, pricing, customers, finance, orders, HR | Monolith (FastAPI) | Strong consistency: sale, stock, payment, customer balance and promo code limit change in one transaction |
| Tenant registry, plans, subscriptions, payments, platform staff, impersonation | Platform and Billing service (Django + DRF) | Control plane: CRUD and staff workflows, Django admin; a separate security boundary from the data plane. The monolith keeps a read-only replica of tenants |
| Notification | Separate service (worker + FastAPI) | Simple, only accepts commands; external providers fail often and the core must never wait for them |
| Analytics | Separate service (FastAPI) | Read-only, heavy queries, separate storage (ClickHouse) |
| Delivery | Separate service (FastAPI) | Real-time, geo, scales independently |
| Audit | Separate service (Django + DRF) | The audit trail must be protected from the service that wrote it; append and read only, the monolith never waits for it. Django: read-only admin for auditors, filtered search API (DRF + django-filter), simple synchronous load |
| Media | Separate service (FastAPI) | Different load (bandwidth and disk), heavy image processing; files never pass through the monolith |
| Supplier portal | Separate service (Django + DRF + HTMX) | Users are outside the tenant and work with several tenants; separate identity and security boundary. Django: lots of auth, forms and CRUD, and the built-in auth system fits a separate identity well |
| Marketplace sync | Separate service (FastAPI + worker) | External APIs are unreliable and rate limited; their problems must not affect the monolith |
| General ledger, installments, production, planning, workflow engine, payroll, reporting, multi-company (part II) | Monolith (FastAPI) | Every one of them posts to the same ledgers and stock as sales, and the journal entry must be in the same transaction as the document that created it |

### Service catalog

| Service | Stage | Stack | Owns (data) | Publishes | Consumes | Sync interfaces |
|---|---|---|---|---|---|---|
| Core (monolith) | 0–13, 17, 19, 26–33 | FastAPI, SQLAlchemy, Postgres, Redis | users, memberships, catalog, stock ledger, POs, sales, customers, finance, orders, tenant replica; part II: journal entries, installment contracts, work orders, payroll runs, report definitions | `sale.*`, `stock.*`, `order.*`, `purchase_order.*`, `payable.*`, `price_list.changed`, `customer.created`, `tenant.provisioned`, `audit.recorded`; part II: `journal_entry.posted`, `installment.overdue`, `work_order.completed`, `replenishment.suggested`, `payroll.posted` | `tenant.*`, `domain.changed`, `entitlements.changed`, `delivery.*`, `media.asset.ready`, `supplier.linked` | back-office, POS sync, storefront API, internal API (commands) |
| Notification | 14 | worker + FastAPI, Postgres, RabbitMQ | templates, messages, recipient preferences | none | `notification.send` commands (RabbitMQ) | status API, provider callbacks |
| Platform and Billing | 15 | Django + DRF, Celery, Postgres | tenants, domains, plans, subscriptions, invoices, payments, platform staff | `tenant.*`, `domain.changed`, `entitlements.changed`, `audit.recorded` | `tenant.provisioned`, `tenant.provisioning_failed` | Django admin, billing API, JWKS, impersonation tokens, payment webhooks |
| Analytics | 16 | FastAPI, Postgres / ClickHouse | read models (projections) | none | `sale.*`, `stock.*`, `order.*`, `customer.created`, `delivery.status_changed` | reports API (JWKS auth) |
| Delivery | 18 | FastAPI, PostGIS, Redis | couriers, zones, quotes, deliveries, courier cash ledger | `delivery.status_changed`, `delivery.failed`, `courier_cash.handed_over`, `audit.recorded` | `order.ready_for_delivery`, `order.status_changed` | quote API, courier app API, tracking WebSocket |
| Audit | 22 | Django + DRF, Postgres | audit records and hash chains | none | `audit.recorded` | search API, read-only admin |
| Media | 23 | FastAPI + worker, MinIO, Postgres | assets and their variants | `media.asset.ready` | owner events for garbage collection (e.g. product archived) | presign, confirm and read APIs |
| Supplier portal | 24 | Django + DRF + HTMX, Postgres | supplier accounts and users, links, PO replica | `supplier.linked`, `audit.recorded` | `purchase_order.*`, `payable.payment_recorded` | portal UI, ERP API; commands to the core |
| Marketplace sync | 25 | FastAPI + worker, Postgres, Redis | connections, credentials, SKU mappings, sync state, conflicts | `audit.recorded` | `stock.changed`, `price_list.changed`, `order.status_changed` | sync dashboard API; commands to the core; marketplace webhooks |

### Event catalog

All events go through Kafka with a versioned envelope (stage 13): `event_id`, `type`, `version`, `tenant_id`, `occurred_at` (UTC), `correlation_id`, `payload`. The key is `tenant_id`, so events of one tenant keep their order.

| Event | Producer | Consumers | Stage |
|---|---|---|---|
| `sale.completed.v1`, `sale.refunded.v1` | Core | Analytics; loyalty (ADR, stage 13) | 13 |
| `stock.changed.v1` | Core | Analytics, Marketplace sync, OpenSearch `[OPT]` | 13 |
| `stock.low.v1` | Core | Analytics; core turns it into a notification command | 13 |
| `customer.created.v1` | Core | Analytics | 13 |
| `tenant.created.v1`, `tenant.updated.v1`, `tenant.status_changed.v1`, `domain.changed.v1` | Platform | Core (replica) | 15 |
| `entitlements.changed.v1` | Platform | Core; Media and Notification (quotas) | 15 |
| `tenant.provisioned.v1`, `tenant.provisioning_failed.v1` | Core | Platform (saga) | 15 |
| `order.ready_for_delivery.v1`, `order.status_changed.v1` | Core | Delivery, Marketplace sync, Analytics | 17 |
| `delivery.status_changed.v1`, `delivery.failed.v1` | Delivery | Core (order state, refund saga), Analytics | 18 |
| `courier_cash.handed_over.v1` | Delivery | Core (finance) | 18 |
| `audit.recorded.v1` | Core, Platform, Delivery, Supplier portal, Marketplace sync | Audit | 22 |
| `media.asset.ready.v1` | Media | Core, Supplier portal | 23 |
| `purchase_order.sent.v1`, `purchase_order.status_changed.v1` | Core | Supplier portal | 24 |
| `payable.payment_recorded.v1` | Core | Supplier portal | 24 |
| `supplier.linked.v1` | Supplier portal | Core | 24 |
| `price_list.changed.v1` | Core | Marketplace sync | 25 |
| `journal_entry.posted.v1` | Core | Analytics (financial dashboards), Audit | 26 |
| `installment.overdue.v1` | Core | Core turns it into a notification command; Analytics | 27 |
| `work_order.completed.v1` | Core | Analytics | 28 |
| `replenishment.suggested.v1` | Core | Analytics; Supplier portal `[OPT]` | 29 |
| `payroll.posted.v1` | Core | Analytics (aggregated only, no personal amounts) | 31 |

**Commands (not events):** `notification.send.v1` goes over RabbitMQ from the core, Platform and Delivery. Calls to the core's internal API (PO confirmation, ASN, marketplace order import, delivery refunds) are synchronous commands with a service token and an `Idempotency-Key`.

### Technology map

| Technology | Stage | Purpose |
|---|---|---|
| FastAPI + Pydantic v2 | from 0 | Monolith, Analytics, Delivery, Media, Marketplace sync |
| SQLAlchemy 2.0 (async) + asyncpg | from 0 | ORM, Unit of Work |
| Alembic | from 0 | Migrations |
| Jinja2 + HTMX | from 0 | Back-office UI |
| Django + DRF + Django admin | 15, 22, 24 | Platform and Billing, Audit, Supplier portal services |
| PostgreSQL | from 0 | RLS, partitioning, FTS, `pg_trgm`, PostGIS |
| Docker, Compose | from 0 | Local environment |
| GitHub Actions | 0 (CI), 21 (CD) | Lint, test, build, deploy |
| JWT, OTP, TOTP | 1, 15 | Auth, 2FA |
| Redis | from 1 | Cache, OTP, rate limiting, distributed locks, pub/sub |
| Celery + RabbitMQ | 9, 15 | Background jobs, import/export, billing schedules |
| FastAPI WebSocket | 9 `[EXT]` | Remote approval, live dashboard |
| React + TypeScript (PWA, IndexedDB) | 12 | Offline POS terminal |
| Kafka | from 13 | Domain event stream |
| ClickHouse | 16 `[OPT]` | Analytical storage |
| OpenSearch | 10 `[OPT]` | Product search (when Postgres is not enough) |
| Prometheus, Grafana, Loki, OpenTelemetry, Sentry | 20 | Observability |
| Kubernetes, Helm | 21 | Deploy |
| PgBouncer | 10 | Connection pooling |
| Locust | 5 | Load testing |
| Pact | 16 | Contract tests between services |
| Playwright | 18 | End-to-end tests |
| MinIO (S3 API) | 23 | File storage, presigned URLs |
| Image processing library (ADR) | 23 | Thumbnails, WebP, EXIF stripping |
| `hypothesis` | 6, 26, 31 | Property-based tests for the pure engines |
| `py-spy`, `memray` | 10 | Profiling and memory leak hunting |
| Terraform or OpenTofu (ADR) | 21 `[EXT]` | Infrastructure as Code |
| PDF rendering library (ADR) | 32 | Invoices, payslips, statements, report exports |

---

# Stages

## Stage 0: Setup
**Prerequisites:** none

- [X] `[CORE]` Repo, branch protection, conventional commits
- [X] `[CORE]` `uv`, `pyproject.toml`, lock file
- [ ] `[CORE]` Modular structure: every domain module has a router, schemas, service, repository, models
- [ ] `[CORE]` Application factory and lifespan (opening and closing connections)
- [X] `[CORE]` Configuration with Pydantic Settings, environment variables, all times UTC and timezone-aware
- [X] `[CORE]` Async SQLAlchemy engine and session, Alembic, Unit of Work foundation
- [ ] `[CORE]` Multi-stage Dockerfile, Compose (Postgres, Redis), healthchecks
- [ ] `[CORE]` Liveness and readiness endpoints
- [ ] `[CORE]` Request lifecycle: middleware order (correlation ID → tenant → auth → error handler), CORS middleware with an explicit origin list; ADR: ASGI vs WSGI, and what the event loop means for blocking calls
- [ ] `[CORE]` Ruff, mypy, pre-commit, pytest (async), httpx, Testcontainers
- [ ] `[CORE]` Test foundation: the test pyramid (unit, integration, e2e) written down in `tests/README.md`; `dependency_overrides` for FastAPI dependencies; fixtures with explicit scope; a fake for every external port; coverage measured in CI as a signal, not a target
- [ ] `[CORE]` CI: lint, mypy, tests, Alembic migration check; the Docker image is the build artifact (tagged by commit SHA)
- [ ] `[CORE]` ADRs: modular monolith; why the monolith is FastAPI and the Platform service is Django; async vs sync; repository and Unit of Work; frontend (back-office Jinja2 + HTMX, POS terminal as a PWA in stage 12)

**Concepts:** application factory, lifespan, dependency injection, settings management, Unit of Work, request lifecycle and middleware, ASGI vs WSGI, test pyramid and dependency overrides, containers and images, CI and build artifacts, packaging (lock file, wheel vs sdist).
**Done when:** `make up` brings the project up, CI is green.

---

## Stage 1: Tenancy, auth and RBAC
**Prerequisites:** 0

### Tenancy
- [ ] `[CORE]` `Tenant`, `Domain`, subdomain validation, tenant-resolving middleware, Redis cache. Tables are designed so that in stage 15 they become a replica fed by the Platform service
- [ ] `[CORE]` `Location` (store and warehouse in one model: `type = store | warehouse`)
- [ ] `[CORE]` Tenant mixin, SQLAlchemy **global filter** (fail closed), `contextvars`
- [ ] `[CORE]` DB roles, RLS (`ENABLE` + `FORCE`), RLS coverage test
- [ ] `[CORE]` Tenant settings: currency, time zone, tax regime, receipt format

### Auth
- [ ] `[CORE]` Global `User` + `Membership`, phone in E.164
- [ ] `[CORE]` Password hashing (Argon2); you build auth **yourself** (no ready-made library)
- [ ] `[CORE]` API standards: single error format, `/api/v1/`, OpenAPI docs
- [ ] `[CORE]` JWT (rotation, reuse detection, tenant claim check), server-side session for the back-office (Redis)
- [ ] `[CORE]` ADR: access token vs refresh token (lifetimes, where the client stores them, what rotation protects against); why a Redis session for the back-office and JWT for the POS; stateless API, no sticky sessions
- [ ] `[CORE]` CSRF protection (you add it yourself for cookie sessions)
- [ ] `[CORE]` Web security baseline (OWASP Top 10): SQL injection (parametrised queries only, a test with hostile input), XSS (autoescape plus a `Content-Security-Policy` header), SSRF (outbound URL validation, needed for stage 19 webhooks), security headers; **least privilege** for DB roles and tokens
- [ ] `[CORE]` Phone OTP (hashing, TTL, attempts, cooldown, atomic check, enumeration protection)
- [ ] `[CORE]` TOTP 2FA (for tenant owners and managers; platform staff 2FA is in Django in stage 15)
- [ ] `[CORE]` Rate limiting (sliding window)

### RBAC
- [ ] `[CORE]` **Permission codes are fixed in code:** `sale.create`, `sale.refund`, `sale.void`, `sale.discount.manual`, `product.read`, `product.update_price`, `inventory.adjust`, `inventory.transfer`, `inventory.transfer.approve`, `purchase.create`, `purchase.approve`, `customer.credit.manage`, `finance.view`, `report.view`, `report.export`, `staff.manage`, `settings.manage`
- [ ] `[CORE]` **Roles are data** (`Role` model, owned by the tenant) holding a set of permissions
- [ ] `[CORE]` Default roles are seeded for a new tenant: Owner, Admin, Branch Manager, Cashier, Warehouse Manager, Accountant, Sales Manager
- [ ] `[CORE]` Location-level access: `Membership` → allowed `Location`s
- [ ] `[CORE]` Permissions through **dependency injection** (the endpoint declares the required permission code), object-level location check, `404` for another tenant or location
- [ ] `[EXT]` Tenants create their own roles. **Privilege escalation protection:** a user can only grant permissions they already have
- [ ] `[EXT]` ADR: RBAC vs ABAC. Location-level access is an attribute check on top of roles; write down where pure RBAC stops being enough (amount limits, ownership, time of day)
- [ ] `[OPT]` OAuth 2.0 / OIDC login through an external identity provider (ADR: when to integrate instead of building)
- [ ] `[CORE]` Role × permission × endpoint matrix test

### Platform operations (temporary, until stage 15)
- [ ] `[CORE]` Tenant creation without UI: an internal CLI command and an endpoint reachable only from the internal network
- [ ] `[CORE]` Tenant creation is designed as an **idempotent command**: in stage 15 it becomes a handler for an event from the Platform service
- [ ] `[CORE]` A separate DB role that bypasses RLS for internal operations, run in a separate process
- [ ] `[CORE]` Invites, audit log (append-only)

**Concepts:** multi-tenancy, RLS, fail-closed filtering, authentication vs authorization, access vs refresh tokens, sessions vs tokens, token rotation, OTP security, hashing and salting, RBAC vs ABAC, OWASP Top 10, least privilege.
**Done when:** tenant isolation, RLS, OTP and RBAC tests are green.

---

## Stage 2: Catalog
**Where:** `modules/catalog` · **Prerequisites:** 1

### Product model
- [ ] `[CORE]` `Category` tree (ADR: adjacency list, materialized path, `ltree`), `Brand`
- [ ] `[CORE]` `Product` and `ProductVariant`: the variant is the sellable unit (SKU). ADR for attributes (color, size): EAV, JSONB or separate tables
- [ ] `[CORE]` **Several barcodes per variant:** a separate `Barcode` table, unique within the tenant, with a type (EAN-13, UPC, QR, internal)
- [ ] `[CORE]` Units of measure; **weighted products:** quantity is `Decimal(12, 3)`
- [ ] `[CORE]` Parsing scale barcodes (weight or price inside a prefixed EAN-13), check digit validation
- [ ] `[CORE]` Archiving (soft delete): a product that has been sold can never be hard-deleted
- [ ] `[EXT]` **Bundle:** a set sold together; on sale, components are deducted from stock
- [ ] `[EXT]` **Kit:** a pre-assembled product with its own stock; the "assemble" operation decreases components and increases the kit. Write the difference from a bundle in an ADR
- [ ] `[EXT]` **Serial-tracked** products: every unit tracked separately (`in_stock`, `sold`, `returned`)
- [ ] `[EXT]` **Batches/lots and expiry dates:** `tracking = none | serial | batch`

### Prices (basics)
- [ ] `[CORE]` `PriceList` and `PriceListItem`: retail (default), wholesale
- [ ] `[CORE]` Location-specific prices (a price list is linked to a location)
- [ ] `[CORE]` Price history
- [ ] `[CORE]` Price changes require `product.update_price` and are written to the audit log

### Search
- [ ] `[CORE]` One search endpoint with priority: barcode (exact) → SKU (exact) → name (`pg_trgm`)
- [ ] `[CORE]` **Search by QR code:** a QR may hold a plain code or a link; extract the product identifier from the scan result and route it to barcode search
- [ ] `[CORE]` Barcode and SKU lookups faster than 10 ms (prove it with indexes)

**Concepts:** polymorphic product model, EAV vs JSONB, constraints, trigram index, check digits.
**Done when:** a cashier finds a product by barcode, scale barcode, SKU or name; location and wholesale prices resolve correctly.

---

## Stage 3: Inventory and warehouses
**Where:** `modules/inventory` · **Prerequisites:** 2

### Stock basics
- [ ] `[CORE]` `StockMovement` ledger (immutable): `receive`, `sale`, `return`, `transfer_out`, `transfer_in`, `adjustment`, `count`, `assembly`
- [ ] `[CORE]` `StockLevel` (location × variant): `on_hand`, `reserved`, `available = on_hand − reserved`; `CHECK` constraints
- [ ] `[CORE]` Minimum stock and reorder level; a low-stock event when stock drops below them
- [ ] `[CORE]` Reconciliation: `on_hand` == sum of movements
- [ ] `[CORE]` Movement history: filters, cursor pagination
- [ ] `[EXT]` Batch and serial movements; **FEFO** (first expired, first out)

### Adjustments and stock counts
- [ ] `[CORE]` Adjustments with reasons: `damaged`, `expired`, `lost`, `found`, `correction`
- [ ] `[CORE]` Adjustments above a set amount require approval
- [ ] `[CORE]` Stock count session: full and partial (cycle count); if sales continue during the count, compute with an initial snapshot and deltas
- [ ] `[CORE]` Variance report → approval → automatic adjustments
- [ ] `[EXT]` Automatic detection of expired batches (Celery beat, after stage 9)

### Transfers and reservations
- [ ] `[CORE]` Transfer request → approval → picking → shipped (**in-transit stock**) → received
- [ ] `[CORE]` Warehouse → store and store → store transfers
- [ ] `[CORE]` Partial receipt and discrepancies (short, damaged)
- [ ] `[CORE]` Reservations with expiry (held sale, e-commerce order, transfer); expired ones are released automatically
- [ ] `[CORE]` Reservation concurrency: two parallel reservations never exceed `available` (a classic race condition; ADR: pessimistic row lock vs atomic `UPDATE ... WHERE available >= :qty`)

### Warehouse operations
- [ ] `[EXT]` Zones and bins inside a warehouse
- [ ] `[EXT]` Receiving → put-away (placing into bins)
- [ ] `[EXT]` **Internal transfer:** moving from bin to bin inside one location; total `on_hand` doesn't change, only the placement does, but a movement is still recorded
- [ ] `[EXT]` Picking list (for transfers and orders), picking route

**Concepts:** ledger, available-to-promise, in-transit stock, state machines, race conditions, pessimistic locking vs atomic updates.
**Done when:** reconciliation matches after any sequence of operations; the parallel reservation test is green.

---

## Stage 4: Procurement
**Where:** `modules/procurement` · **Prerequisites:** 3

- [ ] `[CORE]` `Supplier`: contacts, payment terms
- [ ] `[EXT]` Purchase request: from a location, or automatically from the reorder level
- [ ] `[CORE]` Purchase order states: `draft → pending_approval → approved → sent → partially_received → received → closed / cancelled`
- [ ] `[CORE]` Approval rule based on amount (`purchase.approve`)
- [ ] `[CORE]` Goods receipt: partial receipt, short or excess goods, entering batches and expiry dates, stock movements
- [ ] `[CORE]` **Costing:** weighted average cost (WAC) is recalculated on receipt. Parallel receipts need a lock. ADR: WAC vs FIFO
- [ ] `[CORE]` Returns to supplier
- [ ] `[CORE]` Supplier debt (accounts payable): invoice from receipt, partial payments, balance from a ledger
- [ ] `[CORE]` Purchase history
- [ ] `[EXT]` Supplier performance (lead time, share of discrepancies)
- [ ] `[OPT]` Landed cost: allocating transport costs to item cost

**Concepts:** document workflow, approval flow, costing methods, payables ledger.
**Done when:** after partial receipt, return and payment, stock, cost and debt are correct.

---

## Stage 5: POS sales (the most important stage)
**Where:** `modules/sales` · **Prerequisites:** 4

### Cart
- [ ] `[CORE]` ADR: cart on the server (`Sale` in `draft` state) or on the client. Recommendation: server, because hold and resume need it
- [ ] `[CORE]` Adding by barcode, SKU or search; changing quantity; weighted products
- [ ] `[CORE]` Manual item: not in the catalog, separate permission, doesn't affect stock
- [ ] `[CORE]` Manual discount (line and receipt level): permission and maximum percentage; above the limit, manager approval
- [ ] `[CORE]` **Tax (VAT):** included in or added to the price, product-specific rate, rounding rule (line or receipt level, ADR), snapshot on the line
- [ ] `[CORE]` Holding a sale and resuming it later; hold expiry; ADR: does a hold reserve stock

### Payment
- [ ] `[CORE]` Cash (amount tendered, change), card (terminal reference)
- [ ] `[CORE]` **Split payment** (e.g. 100,000 cash + 200,000 card); on completion `sum(payments) == total`
- [ ] `[CORE]` Customer balance and credit as payment methods (connected in stage 7)

### Completion
- [ ] `[CORE]` One transaction: validation → stock lock (ordered by `variant_id`) → decrement → movements → payments → snapshots (price, cost, tax, discount) → `completed`
- [ ] `[CORE]` `Idempotency-Key`: the response is stored with a TTL, a repeated key with a different payload is a `409`
- [ ] `[CORE]` **Gapless receipt numbers** per location: Postgres sequences have gaps, so use a counter row with a row lock (`with_for_update`). Measure the cost

### Receipt
- [ ] `[CORE]` Receipt output (text for the printer, or PDF)
- [ ] `[CORE]` Electronic receipt: link and QR code (sending by SMS/Telegram in stage 14)
- [ ] `[CORE]` Receipt duplicate: marked "DUPLICATE", written to the audit log

### Post-sale operations
- [ ] `[CORE]` **Void:** cancelling an unfinished sale; fully reversing a completed one within the same shift (`sale.void`, manager approval)
- [ ] `[CORE]` **Refund:** against the original receipt; partial (lines and quantities); you can't return more than was sold minus earlier returns (concurrency for parallel refunds); rules for refunding to the payment method; back to stock or written off as damaged
- [ ] `[CORE]` **Exchange:** return + new sale, linked; the difference is paid or refunded
- [ ] `[EXT]` Returns without a receipt (by policy)

### Manager approval (step-up authorization)
- [ ] `[CORE]` Flow: the cashier sends a request → the manager enters a PIN on the same terminal → the operation runs
- [ ] `[CORE]` PIN is hashed, with an attempt limit
- [ ] `[CORE]` Approval token: single use, bound to the exact operation and amount, valid for 2 minutes
- [ ] `[CORE]` Audit: who requested, who approved, and why
- [ ] `[EXT]` Remote approval: the request arrives on the manager's phone (WebSocket, after stage 9)

### Shifts and cash drawer
- [ ] `[CORE]` Opening/closing a shift; opening cash; cash in and cash out
- [ ] `[CORE]` Expected vs counted cash difference; X and Z reports

### Concurrency and load
- [ ] `[CORE]` Cause a deadlock on purpose and fix it; retries
- [ ] `[CORE]` **Pessimistic vs optimistic locking:** `with_for_update` vs a version column on the stock row; implement both, measure under load, keep one (ADR)
- [ ] `[CORE]` **Isolation level lab:** reproduce a **lost update**, a **non-repeatable read** and a **phantom read** at `READ COMMITTED` and `REPEATABLE READ`; run the sale under `SERIALIZABLE` with retry on serialization failure; explain why `READ UNCOMMITTED` and dirty reads don't exist in Postgres; results in the README
- [ ] `[CORE]` ACID letter by letter on the sale transaction: atomicity (rollback and savepoints when a payment adapter fails), consistency (constraints and the ledger), isolation (the lab above), durability (what `COMMIT` waits for, WAL)
- [ ] `[CORE]` Locust: 50 parallel cashiers; results in the README

**Concepts:** ACID (atomicity, consistency, isolation, durability; commit, rollback, savepoints), pessimistic vs optimistic locking, race conditions, deadlocks, isolation levels and anomalies (dirty, non-repeatable and phantom reads, lost update), idempotency keys, gapless sequences, step-up authorization, tax and rounding, the sale as the hot path and critical path of the system.
**Done when:** under load testing, stock never goes negative and a sale is never written twice; partial refunds, exchanges and voids work correctly.

> **Job search marker:** together with stages 9 and 10, this completes the level 1 MVP. Update your resume and start applying.

---

## Stage 6: Pricing and promotions engine
**Where:** `modules/pricing` · **Prerequisites:** 5

- [ ] `[CORE]` Price resolution order (ADR): customer-specific price → location price → customer group (wholesale) → base retail
- [ ] `[CORE]` `Promotion` model: **conditions** (products, category, brand, location, customer group, minimum quantity or amount, date range, weekdays, time of day) and **benefit** (percentage, fixed amount, fixed price, free item)
- [ ] `[CORE]` Percentage, fixed amount, category and brand discounts
- [ ] `[CORE]` **Buy X Get Y** (2+1 and others): which item is free (usually the cheapest), repeated application on one receipt
- [ ] `[CORE]` Time-based promotions and **happy hour**: in the tenant's time zone
- [ ] `[CORE]` Stacking rules: priority, exclusive promotions, how many promotions per line; the result is **deterministic**
- [ ] `[CORE]` **Coupons** (single-use unique codes) and **promo codes** (shared code, total and per-customer limits)
- [ ] `[CORE]` Promo code limit concurrency: atomic `UPDATE ... WHERE used < limit`; consumed on completion, returned on void
- [ ] `[CORE]` Applied promotions stored as snapshots on sale lines
- [ ] `[CORE]` **Allocating a receipt discount across lines** (largest remainder), so partial refunds produce correct amounts
- [ ] `[CORE]` The engine is a **pure function** (no DB queries inside): input is the cart and the rules, output is the prices
- [ ] `[CORE]` Property-based tests (`hypothesis`): the total is never negative, line amounts sum to the total
- [ ] `[EXT]` Promotion preview (simulation) endpoint

**Concepts:** strategy pattern, rules engine, pure functions, property-based testing, rounding when allocating money.
**Done when:** the result is deterministic for any cart and the property tests are green.

---

## Stage 7: Customers and loyalty
**Where:** `modules/customers` · **Prerequisites:** 6

- [ ] `[CORE]` `Customer` (phone unique within the tenant), groups (retail, wholesale, VIP), purchase history
- [ ] `[CORE]` Attaching a customer to a sale
- [ ] `[CORE]` **Loyalty points** in a ledger: earning, spending, expiry, cancellation on refund
- [ ] `[CORE]` Earning rules; using points as payment or as a discount
- [ ] `[CORE]` **Store credit:** ledger, top-up, payment method at the POS, refunding to the balance
- [ ] `[CORE]` **Customer credit (debt)** with a credit limit: the customer account row is locked so that two terminals selling at the same time can't exceed the limit
- [ ] `[CORE]` Debt repayment, customer account statement
- [ ] `[EXT]` Cashback to balance
- [ ] `[EXT]` Birthday promotions (Celery beat, tenant time zone)
- [ ] `[EXT]` Automatic points expiry

**Concepts:** ledger, balance consistency, account-level locks.
**Done when:** parallel sales never break the credit limit; points and balance are correct after a refund.

---

## Stage 8: Finance
**Where:** `modules/finance` · **Prerequisites:** 7

- [ ] `[CORE]` Payment transaction ledger: sales, refunds, supplier payments, customer payments, expenses
- [ ] `[CORE]` Cash balance per location and shift
- [ ] `[CORE]` Expenses with categories
- [ ] `[CORE]` Reports: revenue, cost of goods sold (COGS, from sale snapshots), gross profit (by period and location)
- [ ] `[CORE]` Accounts receivable (customer debt) and accounts payable (supplier debt), aging analysis (0–30, 31–60, 61–90, 90+ days)
- [ ] `[EXT]` Cash flow report
- [ ] `[EXT]` **Simplified double-entry:** `JournalEntry` and lines; debit = credit guaranteed by the database (deferred constraint trigger); every business document produces its own entries; mistakes are fixed with a reversing entry
- [ ] `[EXT]` Period closing: writing to a closed period is forbidden

**Concepts:** double-entry, immutability, reversal (storno), period closing.
**Done when:** the gross profit report, built from cost snapshots, matches a manually calculated result.

---

## Stage 9: Async jobs, caching and bulk operations
**Where:** `worker/`, `tasks.py` files in modules · **Prerequisites:** 5 (can run in parallel with 6–8)

- [ ] `[CORE]` RabbitMQ broker, Celery; tasks carry `tenant_id`; tasks are sent only **after commit** (the Unit of Work dispatches queued tasks after commit)
- [ ] `[CORE]` Synchronous SQLAlchemy session for workers (Celery is synchronous). ADR: Celery vs async alternatives (arq, taskiq)
- [ ] `[CORE]` Retries with exponential backoff and jitter, `acks_late`, idempotent tasks, separate queues, Celery beat, Flower
- [ ] `[CORE]` Queue mechanics: ack / nack and requeue, prefetch count as **backpressure**, a **poison message** (fails forever) goes to a DLQ after the maximum retries; message queue (work) vs event stream (facts), the ADR that stage 13 builds on
- [ ] `[CORE]` Move OTP and invite sending to Celery
- [ ] `[CORE]` Redis cache (catalog, prices, domains): **cache-aside** (ADR: vs write-through and write-back), TTL, tenant prefix, invalidation on write, hit/miss ratio as a metric
- [ ] `[CORE]` Cache failure modes: **stampede** and thundering herd (lock or early refresh), eviction policy (`maxmemory-policy`, LRU vs LFU), **warm-up** after deploy, hot keys (one tenant's price list)
- [ ] `[CORE]` **Distributed lock** (Redis, with TTL and token): e.g. so a nightly job runs in only one instance. ADR: why stock uses DB locks, not Redis locks; the debate around Redlock
- [ ] `[CORE]` **Import/export:** large CSV/Excel product imports run asynchronously, with progress, an error report, and no duplicates on re-upload (**upsert** with `INSERT ... ON CONFLICT`)
- [ ] `[EXT]` Import progress in the browser: ADR comparing polling, long polling, **SSE** and WebSocket; SSE for one-way progress, WebSocket where the client also sends
- [ ] `[CORE]` **Bulk operations:** bulk price updates, `bulk_create` and RLS
- [ ] `[EXT]` FastAPI WebSocket: remote approval and live dashboard; Redis pub/sub for multiple instances

**Concepts:** queues and caches, at-least-once delivery, ack / requeue / DLQ / poison messages, backpressure, cache patterns (cache-aside, write-through, write-back), TTL and eviction (LRU, LFU), stampede and warm-up, limits of distributed locks, cache invalidation, upsert, push options (polling, long polling, SSE, WebSocket).
**Done when:** no tasks are lost when a worker is restarted; a 100,000-row import passes without memory problems.

---

## Stage 10: Scale, performance and search
**Prerequisites:** 9

- [ ] `[CORE]` Seed: 10M+ sale lines, one very large tenant
- [ ] `[CORE]` `EXPLAIN (ANALYZE, BUFFERS)`: full table scan vs index scan vs bitmap scan, join strategies (nested loop, hash, merge), reading the execution plan; composite, partial, covering (`INCLUDE`), BRIN and GIN indexes; `pg_stat_statements`
- [ ] `[CORE]` SQL lab on real reports: INNER, LEFT, RIGHT and FULL joins, semi and anti joins (`EXISTS`), window functions, `GROUP BY ... FILTER`; one report written three ways with the plans compared
- [ ] `[CORE]` N+1: a test helper that counts queries; eager loading strategies (`selectinload`, `joinedload`); disable lazy loading completely in async (`raise` strategy)
- [ ] `[CORE]` Filtering and sorting only on allowed fields (whitelist); **offset vs cursor pagination** measured at page 10,000
- [ ] `[CORE]` Soft delete and `WHERE deleted_at IS NULL` partial indexes
- [ ] `[CORE]` Partitioning the sales table by month
- [ ] `[CORE]` Summary tables or materialized views: deliberate **denormalization** (ADR: when to break normal form and how the copy is kept consistent)
- [ ] `[CORE]` Hotspots: one very large tenant and one hot key in Redis; what breaks first and how to spread the load (ADR)
- [ ] `[CORE]` **Profiling:** `py-spy` and `memray` on an API worker under load; find one bottleneck and one memory leak that you planted on purpose
- [ ] `[EXT]` **Read replica** for reports: streaming replication in Compose, a read-only session, measuring replication lag and what a stale read means for the user
- [ ] `[CORE]` **Full-text search:** `tsvector` + `pg_trgm`; Uzbek (Latin and Cyrillic) and Russian; Latin–Cyrillic transliteration
- [ ] `[CORE]` PgBouncer: transaction pooling and `SET LOCAL`; the problem with asyncpg prepared statements and its fix
- [ ] `[CORE]` SQLAlchemy connection pool settings: size, overflow, timeout; measure what happens when the pool runs out
- [ ] `[OPT]` OpenSearch: an index synced through events; ADR: when Postgres is not enough

**Concepts:** B-tree, query planner and execution plans, join strategies, normalization vs denormalization, offset vs cursor pagination, partition pruning, FTS, connection pooling, read replicas and replication lag, hotspots and hot keys, profiling, bottlenecks and memory leaks.
**Done when:** before/after results for every report are in the README.

---

## Stage 11: HR (minimal)
**Where:** `modules/hr` · **Prerequisites:** 10

- [ ] `[CORE]` `Employee` (linked to User and Membership), position, location
- [ ] `[CORE]` Hiring: `candidate → interview → offer → hired`; on `hired`, a Membership and role are created
- [ ] `[EXT]` Work schedule, attendance
- [ ] `[EXT]` Cashier KPIs
- [ ] `[OPT]` Extracting HR into a separate Django service as extra Django practice (Django is already used in stages 15, 22 and 24, so there is little new here; only after the Platform service is done; memberships stay in the monolith, so the dependency has to be solved through events)

**Concepts:** state machine, cross-module side effects (creating a Membership), keeping scope small.
**Done when:** the main flow works. Don't expand it.

---

## Stage 12: Offline POS
**Where:** `pos-terminal/` (React + TypeScript PWA), `modules/sync` · **Prerequisites:** 7 and 9

### Terminal
- [ ] `[CORE]` ADR: PWA + IndexedDB or a small desktop app (SQLite)
- [ ] `[CORE]` Device registration: every terminal is bound to a location, with its own device credentials
- [ ] `[CORE]` Downloading a snapshot of catalog, prices, promotions and customers
- [ ] `[CORE]` Incremental sync: `updated_since` cursor, tombstones for deletions

### Offline sales
- [ ] `[CORE]` Sales with a client-generated UUID
- [ ] `[CORE]` Offline receipt numbers with a device prefix (a global gapless number is impossible offline)
- [ ] `[CORE]` **The pricing problem:** the promotions engine is also needed on the client. ADR: sharing rules as data; does the server recalculate, or accept the client's price within a policy
- [ ] `[CORE]` Offline policy: maximum offline duration and amount; are refunds and credit sales allowed offline

### Sync
- [ ] `[CORE]` Client outbox, batch upload, retries with backoff
- [ ] `[CORE]` Server-side idempotency (unique UUID), out-of-order batches
- [ ] `[CORE]` **Conflicts:** stock went negative (the sale physically happened: accept it, flag it, warn), price changed (keep the client price, audit), promo code limit exceeded, credit limit exceeded, product deleted
- [ ] `[CORE]` Clock skew: device time and server time are stored separately
- [ ] `[CORE]` Tests: network loss, duplicate uploads, out-of-order arrival

**Concepts:** local-first, eventual consistency, sync protocol, idempotency, conflict resolution.
**Done when:** a terminal works offline for 1 hour and, after reconnecting, syncs all sales without duplicates and with a conflict report.

---

## Stage 13: Events and preparing for extraction
**Prerequisites:** 12

- [ ] `[CORE]` Module boundaries with `import-linter`
- [ ] `[CORE]` Removing cross-module JOINs and FKs with parts that will be extracted
- [ ] `[CORE]` Domain events: `sale.completed.v1`, `sale.refunded.v1`, `stock.changed.v1`, `stock.low.v1`, `order.ready_for_delivery.v1`, `customer.created.v1`
- [ ] `[CORE]` Event envelope, schemas, versioning; backward-compatible changes (adding optional fields) vs breaking changes (a new version with parallel consumers)
- [ ] `[CORE]` ADR: delivery semantics. At-most-once vs at-least-once vs "exactly-once"; why the outbox on the producer side plus an idempotent consumer (**inbox pattern**, a processed-events table) is the practical answer
- [ ] `[CORE]` **Sync vs async boundary** (ADR). After `SaleCompleted`:

```
Inside the sale transaction (sync):   stock, payments, promo code, credit limit
Through outbox → Kafka (async):       electronic receipt, notifications, analytics,
                                      financial entries [EXT], loyalty (ADR)
```

- [ ] `[CORE]` Transactional outbox, relay (`FOR UPDATE SKIP LOCKED`)
- [ ] `[CORE]` Kafka (KRaft), partitioning by `tenant_id`
- [ ] `[CORE]` Correlation ID, structlog
- [ ] `[CORE]` CI builds several images

Later stages add their own events; the full list is in the **Event catalog**.

**Concepts:** module boundaries, bounded contexts, domain events, transactional outbox and inbox, delivery semantics, event versioning and schema compatibility, partitioning and ordering, sync vs async boundary.
**Done when:** the "Conditions for extracting a microservice" are fully met.

---

## Stage 14: Notification service
**Where:** `services/notification` · **Prerequisites:** 13

**Why a separate service (ADR):** sending messages is slow, depends on external providers and fails often. The core only says "send this" and never waits: if the SMS provider is down, sales keep working. It is also the simplest service, so it is the safest place to learn consumers, DLQs and idempotency before the harder services.

### Foundation
- [ ] `[CORE]` A Python worker (RabbitMQ consumer) plus a small FastAPI app for health checks and the status API; own Postgres; Docker, CI and test standards the same as the core
- [ ] `[CORE]` Command contract `notification.send.v1`: `message_id` (idempotency key), tenant, recipient, channel, template code, variables, locale, priority; a versioned schema

### Delivery pipeline
- [ ] `[CORE]` Channels behind provider adapters: SMS, Telegram, email; fakes for tests; real providers checked against their official docs
- [ ] `[CORE]` Templates: platform defaults overridable per tenant, locales (uz-Latn, uz-Cyrl, ru), variables validated before sending, template versions; a sent message stores the rendered text as a snapshot
- [ ] `[CORE]` Message state machine: `queued → sending → sent → delivered / failed`; attempts are logged; provider delivery callbacks update the status
- [ ] `[CORE]` Idempotent consumer (unique `message_id`), at-least-once delivery from RabbitMQ, acknowledge only after the attempt is recorded
- [ ] `[CORE]` Retries with exponential backoff through delay queues (TTL + dead-letter exchange), DLQ after the maximum attempts, a tool to replay the DLQ
- [ ] `[CORE]` Priority queues (OTP before receipts before marketing), per-provider outbound rate limits and a circuit breaker
- [ ] `[CORE]` Sending electronic receipts (the link and QR code from stage 5)
- [ ] `[CORE]` Messages from the Platform service: invites to tenant owners, payment reminders
- [ ] `[CORE]` Removing the old code from the core: OTP and invites (stage 9) now go through this service

### Recipients and privacy
- [ ] `[CORE]` Recipient preferences: preferred channel, opt-out of marketing (transactional messages such as OTP and receipts always go out)
- [ ] `[CORE]` Privacy: phone numbers and emails masked in logs, a retention period for message bodies
- [ ] `[EXT]` Fallback channel: if Telegram fails or the user hasn't linked it, send an SMS
- [ ] `[EXT]` Quiet hours for non-urgent messages, in the tenant's time zone
- [ ] `[EXT]` Cost tracking per tenant (SMS count), a quota through Platform entitlements
- [ ] `[EXT]` Telegram bot for tenant owners: daily report

**Concepts:** commands vs events, at-least-once delivery and idempotent consumers, DLQ and delayed retries, provider adapters, message state machine.
**Done when:** with the SMS provider down for 10 minutes, no message is lost or sent twice: messages retry and go out after recovery, those that run out of attempts land in the DLQ and can be replayed, and the core never waits for a send.

---

## Stage 15: Platform and Billing service (Django + DRF)
**Where:** `services/platform` · **Prerequisites:** 14

**Why Django (ADR):** this service is the SaaS control plane. It is mostly CRUD and staff workflows, the load is synchronous, and Django admin, auth, ORM and migrations save the most time here. You also get to compare both frameworks on a real task in one project.

### Foundation
- [ ] `[CORE]` Django project, separate PostgreSQL database, DRF, split settings; Docker and CI standards the same as the monolith
- [ ] `[CORE]` Django structure: apps, each with a service layer (business logic not in views and serializers)
- [ ] `[CORE]` pytest-django, factory_boy, Testcontainers
- [ ] `[CORE]` Celery with Django integration (RabbitMQ broker)

### Django admin and platform staff
- [ ] `[CORE]` Django admin for platform staff: custom AdminSite, only on a separate host
- [ ] `[CORE]` Permissions with Django's built-in **Group and Permission** system. Write the difference from the monolith's RBAC in an ADR: here staff are global, not split by tenant, so the built-in system fits exactly
- [ ] `[CORE]` Mandatory TOTP 2FA for platform staff
- [ ] `[CORE]` Custom admin actions and views: suspending a tenant, changing a plan, MRR dashboard
- [ ] `[CORE]` Audit log: Django admin log plus your own audit table

### Moving ownership of the tenant registry
- [ ] `[CORE]` Tenant, Domain and plans now **belong to this service** (ADR, strangler fig). The monolith keeps only a read-only replica of them
- [ ] `[CORE]` Events: `tenant.created.v1`, `tenant.updated.v1`, `tenant.status_changed.v1`, `domain.changed.v1`, `entitlements.changed.v1`
- [ ] `[CORE]` An idempotent consumer in the monolith that updates the replica; version check for out-of-order events
- [ ] `[CORE]` The cost of eventual consistency: a new tenant's subdomain works only after the event is processed; a page for the intermediate `provisioning` state
- [ ] `[CORE]` Migrating existing tenants: a one-off migration, then comparing results on both sides

### Tenant provisioning saga (orchestration)
- [ ] `[CORE]` Flow: an admin creates a tenant → Platform stores it as `provisioning` → event → the monolith creates the default location, roles, owner and membership → `tenant.provisioned.v1` or `tenant.provisioning_failed.v1` → Platform activates the tenant and sends an invite through Notification
- [ ] `[CORE]` Timeouts, retries and compensating steps
- [ ] `[CORE]` ADR: **orchestration** here (Platform drives it), **choreography** in Delivery. Compare the two
- [ ] `[CORE]` If the monolith is down during provisioning, the saga completes on its own after it recovers

### Billing
- [ ] `[CORE]` `Plan`, `Subscription`, `Invoice`, `Payment`: models, DRF API and admin
- [ ] `[CORE]` Tenant state machine (`trial → active → past_due → suspended → cancelled`); every transition emits an event, and the monolith shows the `suspended` page through the replica
- [ ] `[CORE]` **Entitlements:** plan limits (locations, staff, terminals) and feature flags are sent to the monolith by event, and the monolith checks them locally. ADR: why the monolith doesn't call Platform synchronously on every request
- [ ] `[CORE]` Payme/Click webhooks in DRF: signature, idempotency, amounts in tiyin (check the providers' official docs)
- [ ] `[CORE]` Celery beat: invoice generation, reminders, grace period, automatic suspension
- [ ] `[CORE]` Payment reconciliation

### Impersonation and service-to-service auth
- [ ] `[CORE]` Impersonation: Platform issues a short-lived token signed with an asymmetric key; the monolith verifies it through JWKS and marks the session as "impersonated"; audit on both sides
- [ ] `[CORE]` Service tokens for the Platform ↔ monolith internal API
- [ ] `[EXT]` Service-to-service mTLS

### DRF concepts
- [ ] `[CORE]` ViewSets and routers, serializers, permission classes, throttling, django-filter, drf-spectacular
- [ ] `[CORE]` ADR: DRF serializers vs Pydantic, DRF permission classes vs FastAPI dependencies, Django ORM vs SQLAlchemy. Compare with real experience on both sides
- [ ] `[EXT]` **Self-service signup:** public DRF endpoint → trial tenant; phone OTP, rate limiting, abuse protection

**Concepts:** control plane vs data plane, moving data ownership, replication through events, orchestration saga, entitlements, comparing Django and FastAPI.
**Done when:** a tenant created in Django admin starts working on its own subdomain without any manual steps; a tenant that doesn't pay is suspended in the monolith automatically through events; if the monolith is down during provisioning, the saga completes after it recovers.

---

## Stage 16: Analytics service (FastAPI)
**Where:** `services/analytics` · **Prerequisites:** 15

**Why a separate service (ADR):** analytics only reads. Its queries scan millions of sale lines and must not slow down sales in the core database. A delay of a few seconds is acceptable, and it needs a different storage model (columnar for heavy aggregations). So it builds its own read models from events.

### Infrastructure
- [ ] `[CORE]` FastAPI, async SQLAlchemy, Alembic, separate database
- [ ] `[CORE]` Kafka consumer, commit the offset after writing, replay
- [ ] `[CORE]` Idempotent projections: every event applied exactly once (`event_id`), out-of-order and late events, refunds correcting earlier figures
- [ ] `[CORE]` Tenant isolation in every query (`404` for another tenant); "today" and "this week" computed in the tenant's time zone
- [ ] `[CORE]` Strangler fig: run in parallel with the monolith's reports, compare, switch over
- [ ] `[CORE]` JWT through JWKS (RS256), Pact contract tests
- [ ] `[OPT]` **ClickHouse:** MergeTree, materialized views; comparison with Postgres (ADR)

### Dashboard
- [ ] `[CORE]` Today's revenue, profit, receipt count, average receipt, products sold, share of returns (near real-time from events)

### Deep analysis
- [ ] `[CORE]` Sales by location, cashier, category, product, hour, weekday
- [ ] `[CORE]` Profit by product, top customers
- [ ] `[CORE]` Slow-moving and "dead" stock
- [ ] `[CORE]` Inventory turnover
- [ ] `[CORE]` ABC analysis
- [ ] `[EXT]` Low-stock forecast (moving average or exponential smoothing), reorder suggestions

**Concepts:** read models and CQRS, event replay, idempotent projections, columnar storage, strangler fig.
**Done when:** the database can be rebuilt from scratch from events and the results match the monolith.

---

## Stage 17: E-commerce channel
**Where:** `modules/orders` (monolith), storefront API under `/api/storefront/v1/` · **Prerequisites:** 16

**Why inside the monolith (ADR):** an online order and a POS sale sell from the same stock. Reserving and decrementing must happen in the same transaction as the stock row lock, otherwise the last item gets sold twice. So orders live in the monolith; only the storefront frontend is separate.

### Storefront API
- [ ] `[CORE]` A public storefront API per tenant (tenant resolved by domain), separate from the back-office API: only published products, the selling price (never cost), availability shown as "in stock / low / out of stock" rather than exact quantities (ADR: why not expose exact numbers)
- [ ] `[CORE]` Publishing: an `is_online` flag on products, an online price list (sales channel), which locations' stock is visible online
- [ ] `[CORE]` Catalog browsing: categories, facet filters (brand, price range, attributes), full-text search from stage 10, cursor pagination
- [ ] `[CORE]` Caching: HTTP caching (`ETag`, `Cache-Control`) and a Redis cache invalidated on price and stock changes
- [ ] `[CORE]` CORS for a storefront SPA (allowed origins per tenant domain, preflight caching); versioning and backward-compatibility rules for a public API; ADR: REST here, where RPC or GraphQL would fit, and why not
- [ ] `[EXT]` SEO: slugs, sitemap, canonical URLs
- [ ] `[OPT]` A minimal storefront UI (Jinja2 + HTMX) to demo the whole flow

### Customer accounts
- [ ] `[CORE]` Customer login with phone OTP (reusing stage 1), linked to `Customer` from stage 7: the same phone means the same customer, so loyalty is shared between the POS and online
- [ ] `[CORE]` Guest checkout; address book
- [ ] `[EXT]` Spending loyalty points and store credit online

### Cart and checkout
- [ ] `[CORE]` Server-side cart: an anonymous cart token, merged into the account on login; prices recalculated on every change through the pricing engine (stage 6). Client prices are never trusted
- [ ] `[CORE]` Checkout: address, fulfillment method (delivery or pick up in store, BOPIS), delivery price (from the Delivery service after stage 18, a flat rate until then), promo code, totals with tax snapshots
- [ ] `[CORE]` If a price or promotion changed between cart and checkout, the customer sees the new total and confirms it again
- [ ] `[CORE]` Order creation: `Idempotency-Key`; stock reservation with TTL in the same transaction (stage 3); price, tax and promotion snapshots on order lines

### Payment
- [ ] `[CORE]` Online payment (Payme/Click behind a `PaymentProvider` interface, which stage 19 later generalizes; check the providers' official docs) and cash on delivery
- [ ] `[CORE]` Payment webhook: signature check, idempotency, amount check in tiyin, transition `pending_payment → paid`
- [ ] `[CORE]` The reservation of an unpaid order is released automatically after the TTL (Celery beat) and the order becomes `cancelled`. ADR: what happens to a payment that arrives after expiry (automatic refund or re-reserve if stock is still there)

### Order lifecycle and fulfillment
- [ ] `[CORE]` Order state machine: `pending_payment → paid → picking → packed → ready_for_pickup / ready_for_delivery → shipped → delivered / picked_up → completed`, plus `cancelled` and `returned`; transitions go through a transition function and are logged
- [ ] `[CORE]` Choosing the fulfilling location (warehouse or nearest store with stock). ADR: no splitting vs split shipments
- [ ] `[CORE]` Picking list and packing in the back-office. ADR: when stock is decremented (on payment or on shipment) and how the reservation turns into a `sale` movement
- [ ] `[CORE]` Oversell prevention: the POS and online try to sell the last item at the same time (the same lock order as stage 5); a test that proves it
- [ ] `[CORE]` A ready order emits `order.ready_for_delivery.v1`; for BOPIS the customer is notified and picks up with a code
- [ ] `[CORE]` Customer notifications through the Notification service: order confirmed, ready, shipped, delivered
- [ ] `[CORE]` Order permissions: `order.fulfill`, `order.cancel`, `order.refund`; sensitive operations go to the audit log

### After-sales
- [ ] `[CORE]` Cancellation: by the customer before picking, by staff at any point before shipping; the reservation is released and the payment refunded
- [ ] `[CORE]` Online returns: request → approval → item received → refund to the original payment method; back to stock or written off as damaged; reuses the refund rules from stage 5 (can't return more than was sold)
- [ ] `[EXT]` Order history and tracking page for the customer
- [ ] `[EXT]` Abandoned cart reminders (Celery beat, Notification service)

**Concepts:** sales channels, reservation with TTL, payment webhook idempotency, order state machine, fulfillment, oversell prevention.
**Done when:** an online order goes from cart to delivered (or picked up) and returned, with correct stock, payments and reservations at every step; the parallel POS + online last-item test never oversells; unpaid orders release their stock automatically.

---

## Stage 18: Delivery service (FastAPI)
**Where:** `services/delivery`, `courier-app/` (PWA) · **Prerequisites:** 17

**Why a separate service (ADR):** it is real-time (courier locations every few seconds, thousands of WebSocket connections), geo-heavy (PostGIS, Redis GEO), and scales with the number of active couriers rather than the number of sales. It talks to the core only through events and commands (choreography).

### Foundation
- [ ] `[CORE]` FastAPI, async SQLAlchemy, its own PostGIS database, Redis; Docker, CI and test standards the same as the other services
- [ ] `[CORE]` Couriers: `Courier` (belongs to a tenant), status (`offline / available / busy`); courier app (PWA) login with phone OTP and device binding

### Zones and pricing
- [ ] `[CORE]` Delivery zones as polygons per location; point-in-polygon check for an address; an address outside every zone is not deliverable
- [ ] `[CORE]` Delivery price quote: by zone or distance, minimum order amount, free delivery threshold; the storefront checkout (stage 17) asks for a quote; the quote has an ID and a TTL, and its price is stored on the order as a snapshot

### Dispatch
- [ ] `[CORE]` A delivery is created from `order.ready_for_delivery.v1` (idempotent by order ID)
- [ ] `[CORE]` Nearest available courier (Redis GEO or PostGIS), an offer with a timeout, then the next courier
- [ ] `[CORE]` **Atomic acceptance:** two couriers accept the same delivery at once, only one wins (`UPDATE ... WHERE status = 'offered'`); a test that proves it
- [ ] `[EXT]` Batching several orders into one route

### Tracking
- [ ] `[CORE]` Delivery state machine: `created → offered → assigned → picked_up → in_transit → delivered / failed → returned_to_store`; transitions logged and published as `delivery.status_changed.v1`
- [ ] `[CORE]` Courier location updates: throttled on the client, current position in Redis GEO, sampled history in PostGIS
- [ ] `[CORE]` ADR: SSE vs WebSocket vs long polling for tracking (the customer only reads, the back-office also sends)
- [ ] `[CORE]` WebSocket tracking for the customer and the back-office; Redis pub/sub across several instances; reconnects and missed updates
- [ ] `[CORE]` A courier going offline in the middle of a delivery: timeout, then reassignment
- [ ] `[EXT]` ETA (distance and average speed at first)

### Handover and cash
- [ ] `[CORE]` Handover confirmation with an OTP sent to the customer (through Notification)
- [ ] `[CORE]` Cash on delivery: the courier collects cash → courier cash ledger → handed over at the store → `courier_cash.handed_over.v1` → reconciled in finance (stage 8)
- [ ] `[EXT]` Proof of delivery photo (through the Media service, after stage 23)

### Failure saga
- [ ] `[CORE]` Choreography saga: failed delivery → `delivery.failed.v1` → the core cancels the order and refunds the payment → stock goes back to the location when the courier returns the item. Every step is idempotent and survives a restart of any participant
- [ ] `[CORE]` ADR: choreography here vs orchestration in stage 15; who knows the whole flow, and how you debug it

### Quality
- [ ] `[CORE]` Contract tests for events and the quote API (Pact); audit events for sensitive operations
- [ ] `[CORE]` Playwright e2e: order → delivery → confirmation

**Concepts:** geo queries, real-time push, atomic assignment, choreography saga, cash ledger.
**Done when:** an online order is delivered end to end with live tracking; two couriers accepting the same delivery never both win; a failed delivery automatically refunds and returns stock, even if the core was down when it failed.

---

## Stage 19: Integrations
**Where:** `modules/integrations` · **Prerequisites:** 18 (parts can be done earlier)

- [ ] `[CORE]` Adapter pattern: `PaymentProvider`, `FiscalProvider`, `SmsProvider`, `ReceiptPrinter` interfaces; fakes for tests
- [ ] `[CORE]` Timeouts, retries with exponential backoff and jitter, circuit breaker, **bulkhead** (a separate pool and queue per provider), **graceful degradation** (card payment unavailable, cash still works)
- [ ] `[CORE]` **Outbound webhooks** to tenant systems: signatures, retries, delivery log
- [ ] `[EXT]` Card and QR payment providers at the POS
- [ ] `[EXT]` Fiscal integration: check the current requirements in Uzbekistan; adapter and mock
- [ ] `[EXT]` Receipt printer (ESC/POS), barcode scanner (keyboard mode), electronic scale
- [ ] `[EXT]` Export to accounting systems (e.g. file formats for 1C)

**Concepts:** anti-corruption layer, ports and adapters, circuit breaker, bulkhead, graceful degradation, fallback, SSRF on outbound calls, unreliability of external systems.
**Done when:** every external call goes through an adapter that has a fake; when a fake provider times out, the circuit breaker opens and the POS keeps selling (card payment shows as unavailable, cash still works); outbound webhooks are retried and the delivery log shows every attempt.

---

## Stage 20: Observability
**Prerequisites:** 19 (covers every service built so far; later services add themselves as they are built)

- [ ] `[CORE]` Correlation ID across HTTP, Kafka, RabbitMQ and Celery, in every service (FastAPI and Django)
- [ ] `[CORE]` OpenTelemetry tracing: FastAPI, Django, SQLAlchemy, Django ORM, httpx, Celery, Kafka, RabbitMQ; one trace follows a sale from the POS through the outbox to Analytics and Notification
- [ ] `[CORE]` Prometheus: RED metrics per service, business metrics (sales per minute, failed payments, oversell conflicts), outbox backlog, consumer lag per consumer group, queue length, DLQ size, offline terminal sync delay
- [ ] `[CORE]` Structured logging contract: JSON, correlation ID, tenant, log levels, no personal data; what goes to logs vs metrics vs traces. Centralized logs with **Loki**
- [ ] `[CORE]` Grafana: a platform overview dashboard and one per service; alerts with runbooks; symptom-based alerting so there is no **alert fatigue**; Sentry for errors
- [ ] `[CORE]` **SLI vs SLO vs SLA:** p50 / p95 / p99 and tail latency, throughput, success rate for sale completion; error budgets and what a burnt budget changes in priorities
- [ ] `[CORE]` Liveness and readiness in every service; synthetic checks for key flows (login, sale, storefront checkout)
- [ ] `[CORE]` Chaos experiments and postmortems

**Concepts:** traces, metrics and logs, structured logging, distributed tracing, RED and USE methods, latency percentiles and tail latency, throughput, SLI / SLO / SLA and error budgets, alert fatigue, context propagation.
**Done when:** one sale can be followed in a single trace across the core, Kafka, Notification and Analytics; stopping a consumer triggers a lag alert that links to a runbook; every chaos experiment has a written postmortem.

---

## Stage 21: Kubernetes and CD
**Prerequisites:** 20

- [ ] `[CORE]` k3d/kind, Helm charts: one chart per service on top of a shared library chart (or an umbrella chart for the whole shopStack)
- [ ] `[CORE]` Stateful dependencies (Postgres per service, Kafka, RabbitMQ, Redis, MinIO). ADR: run them in the cluster with operators or use managed services
- [ ] `[CORE]` Wildcard ingress, cert-manager (DNS-01), host-based routing (tenant subdomains, `suppliers.`, `admin.`, `courier.`, `media.`)
- [ ] `[CORE]` Secrets (ADR: sealed secrets or an external secrets manager), **secret rotation** without downtime (DB password, JWT keys through JWKS), resource limits, probes, a migration Job per service (Alembic and Django `migrate`)
- [ ] `[CORE]` Deployment strategies (ADR): **rolling** (default), **blue-green** and **canary**; what each costs with database migrations; a rehearsed **rollback**
- [ ] `[CORE]` Stateless services: no local state, sessions in Redis, no sticky sessions; horizontal vs vertical scaling measured on the API and on Postgres
- [ ] `[CORE]` **High availability:** list every single point of failure (Postgres, Redis, RabbitMQ, Kafka, ingress); Postgres failover (replica and promotion, ADR: operator vs managed); **leader election** for singletons (Celery beat, outbox relay) with a Kubernetes lease or a Redis lock
- [ ] `[EXT]` **Infrastructure as Code:** the cluster and managed services in Terraform/OpenTofu (ADR); immutable infrastructure, no manual changes
- [ ] `[CORE]` Network policies: every service reaches only what it needs; the core's internal API is never exposed through the ingress
- [ ] `[CORE]` Zero-downtime migrations with expand/contract
- [ ] `[CORE]` HPA (CPU, requests per second) and KEDA (queue length, consumer lag)
- [ ] `[CORE]` CD: one image per service, only changed services are deployed; staging → approval → production
- [ ] `[CORE]` Actually test backup and restore: every database and MinIO, on a fresh cluster
- [ ] `[CORE]` Deploy to a real VPS or cloud
- [ ] `[OPT]` GitOps with ArgoCD

**Concepts:** declarative deployment, rolling / blue-green / canary and rollback, autoscaling and load balancing, stateless vs stateful, high availability, SPOF, failover, leader election, secret management and rotation, Infrastructure as Code, immutable infrastructure, expand/contract migrations, backup and restore.
**Done when:** the whole shopStack (core, every service, workers) deploys to staging through one pipeline and is promoted to production after approval; a migration runs with zero downtime under load; a restore from backup is proven on a fresh cluster.

---

## Stage 22: Audit service (Django + DRF)
**Where:** `services/audit` · **Prerequisites:** 15

**Why a separate service (ADR):** the audit trail must be protected from the service that wrote it: an attacker inside the monolith, or a bad migration, must not be able to delete audit records. The service only appends and reads, and the monolith never waits for its response.

**Why Django + DRF (ADR):** the service's main job is a filtered search API and a viewing interface for auditors and platform staff. DRF (ViewSet, django-filter, `CursorPagination`) and a read-only Django admin give you these with the least code. The load is synchronous and simple, so async brings no benefit. The cost: the Django ORM doesn't know about append-only tables, triggers or partitioning, so they are written by hand in `RunSQL` migrations.

### Foundation
- [ ] `[CORE]` Django project, separate PostgreSQL database, DRF; split settings, Docker, CI and test standards (pytest-django, factory_boy, Testcontainers) the same as the Platform service in stage 15
- [ ] `[CORE]` Kafka consumer as a **management command** (`manage.py consume_audit`) in a separate process; graceful shutdown; the offset is committed only after the records are committed

### Ingestion
- [ ] `[CORE]` Audit event envelope `audit.recorded.v1`: who (actor, impersonator), what (action, permission code), which object, before and after, reason, approving manager, correlation ID, IP, device
- [ ] `[CORE]` The monolith emits audit events through the outbox: a sensitive operation and its audit event are in one transaction, so audit is never lost
- [ ] `[CORE]` Idempotent ingestion (unique constraint on `event_id`), duplicate and out-of-order events; batch writes (`bulk_create`) and measuring their cost

### Immutable storage
- [ ] `[CORE]` Append-only: the DB role the service runs under has no `UPDATE` or `DELETE` privileges, plus a trigger that rejects them; both in `RunSQL` migrations
- [ ] `[CORE]` Monthly partitioning (`RunSQL`), a Celery beat task that creates future partitions in advance
- [ ] `[CORE]` The Django model is immutable: `save()` only for new records, `delete()` and queryset `update()`/`delete()` forbidden; protection exists both in the ORM and in the database (explain in an ADR why both are needed)
- [ ] `[CORE]` **Hash chain:** a chain of records per tenant (`prev_hash`, `hash`) over canonical JSON; Kafka is partitioned by `tenant_id`, so within a tenant there is a single writer and order is preserved
- [ ] `[CORE]` A Celery beat job that verifies the chain and alerts on breaks; a test that tampers with a record on purpose and shows it gets detected

### Search API and admin
- [ ] `[CORE]` DRF `ReadOnlyModelViewSet`: filters by actor, object, action and period (django-filter), `CursorPagination`, drf-spectacular docs
- [ ] `[CORE]` Auth: the monolith's JWT is verified through JWKS (a custom DRF authentication class); tenant isolation in the permission class and the queryset (fail closed), `404` for another tenant
- [ ] `[CORE]` **Read-only Django admin** for auditors and platform staff: add, change and delete permissions fully disabled; fast changelist for a large table (`show_full_result_count`, indexes)
- [ ] `[CORE]` Platform staff follow the same rules as in the Platform service: mandatory TOTP 2FA, separate host

### Integration
- [ ] `[CORE]` Connecting the audit of the Platform (Django) and Delivery services as well
- [ ] `[CORE]` Strangler fig: write in parallel with the monolith's audit table, compare, move the back-office audit page to the service API
- [ ] `[EXT]` Signing the daily chain root hash with an asymmetric key and storing it outside the service (anchoring)
- [ ] `[EXT]` Signed exports for auditors (Celery task, streaming for large volumes)
- [ ] `[EXT]` Retention policy and archiving old partitions
- [ ] `[OPT]` The conflict between a request to erase personal data and immutability: crypto-shredding (ADR)

**Concepts:** tamper-evident log, hash chain, append-only storage, at-least-once and idempotency, raw SQL migrations in Django, read-only admin.
**Done when:** if one audit record is changed manually in the database, the verification job detects it; records can't be changed or deleted through the admin or the API; no audit record is lost when the monolith or the audit service is restarted.

---

## Stage 23: Media service (FastAPI)
**Where:** `services/media` · **Prerequisites:** 14

**Why a separate service (ADR):** file load is different (bandwidth and disk, not CPU), and image processing is heavy. If large files pass through the monolith, its workers get busy and sale requests slow down.

- [ ] `[CORE]` MinIO (S3 API) in Compose, separate database; ADR: S3 client library and image library (additions to the stack)
- [ ] `[CORE]` `Asset` model and state machine: `pending → uploaded → processing → ready / failed → deleted`
- [ ] `[CORE]` **Presigned upload:** the client uploads the file directly to storage; size and content-type limits (POST policy), short TTL
- [ ] `[CORE]` Upload confirmation: the object exists, its real size, type check by magic bytes (the extension is never trusted)
- [ ] `[CORE]` Tenant isolation: key prefix `tenants/{tenant_id}/...`, `404` for another tenant's asset
- [ ] `[CORE]` Image processing worker: thumbnails, WebP, EXIF stripping, decompression bomb protection (maximum pixel count)
- [ ] `[CORE]` Public and private files: product images are public (cache headers, ETag); import files and invoices only through short-lived presigned GETs
- [ ] `[CORE]` The monolith stores only `asset_id`; `media.asset.ready.v1` event; connecting catalog product images
- [ ] `[CORE]` Orphan cleanup: unfinished uploads (lifecycle rule) and assets nobody uses anymore (garbage collection)
- [ ] `[CORE]` Moving import files (stage 9) and PDF receipts to the media service
- [ ] `[EXT]` Storage quota per plan (through Platform entitlements), counted atomically
- [ ] `[EXT]` Content-based dedup (sha256)
- [ ] `[OPT]` Antivirus scanning for private files (ClamAV)
- [ ] `[OPT]` CDN and cache invalidation

**Concepts:** object storage, presigned URLs, asynchronous processing, file upload security, garbage collection.
**Done when:** a 50 MB file is uploaded without touching the monolith; a file with a fake extension is rejected; unfinished uploads are cleaned up automatically.

---

## Stage 24: Supplier portal (Django + DRF + HTMX)
**Where:** `services/supplier-portal` · **Prerequisites:** 15 and 23

**Why a separate service (ADR):** the users are outside the tenant: one supplier company works with several tenants. The auth model, security boundary and host are completely different from the monolith's.

**Why Django + DRF (ADR):** most of the service is auth, forms, CRUD and pages. Django's built-in auth system (custom user model, sessions, password validation, CSRF), forms and templates save the most time here. DRF provides the API that suppliers' own systems (ERP) connect to. You built auth and CSRF yourself in the monolith; here you compare that with a ready-made system. The cost: a second Django service, and maintaining two different ORMs and migration systems.

### Foundation and identity
- [ ] `[CORE]` Django project, separate database, DRF, separate host (`suppliers.<domain>`); standards the same as the Platform service
- [ ] `[CORE]` UI: Django templates + HTMX (the same approach as the back-office, but Django templates instead of Jinja2; write the difference in an ADR)
- [ ] `[CORE]` **Custom user model** (`AUTH_USER_MODEL`) before the first migration: `SupplierUser`, login by phone in E.164; `SupplierAccount` (a global company). An identity fully separate from tenant users and platform staff
- [ ] `[CORE]` Login: password (Django's hashers, Argon2) and phone OTP (custom authentication backend), sessions, Django CSRF; rate limiting
- [ ] `[CORE]` **Linking:** a tenant sends an invite for its own `Supplier` record (event or internal API) → the supplier accepts → `SupplierLink(tenant_id, supplier_id, supplier_account_id)` → `supplier.linked.v1` to the monolith

### Cross-tenant authorization
- [ ] `[CORE]` Every request is filtered by links (fail closed): a custom manager or queryset; with no link the result is `404`, not an empty list. Template views and DRF views use the same layer
- [ ] `[CORE]` A supplier sees only POs sent to them; the tenant's other data (other suppliers, cost, margin, selling price) never reaches the replica at all
- [ ] `[CORE]` Isolation tests: two tenants and two suppliers, a "foreign object → `404`" matrix for every endpoint and every page

### Purchasing flow
- [ ] `[CORE]` PO replica from events (`purchase_order.sent.v1`, `purchase_order.status_changed.v1`), management command consumer, version check; the monolith stays the owner
- [ ] `[CORE]` Confirming a PO or proposing a change (quantity, date): a command to the monolith's internal API with a service token and `Idempotency-Key`; the monolith's state machine makes the decision (e.g. if the tenant cancelled in parallel, it's rejected and shown in the portal)
- [ ] `[CORE]` Advance shipping notice (ASN): what was shipped and when; the goods receipt in the monolith is pre-filled
- [ ] `[CORE]` Invoice upload (presigned upload through the media service) → a draft payables invoice in the monolith
- [ ] `[CORE]` Viewing payment status (from payables ledger events)

### API and security
- [ ] `[CORE]` DRF API for supplier ERPs: ViewSets, serializers, API keys (hashed, bound to a `SupplierAccount`, revocable), throttling, drf-spectacular
- [ ] `[CORE]` Audit (to the audit service through the outbox), Pact contract tests (the monolith's internal API and events)
- [ ] `[EXT]` Three-way match: PO, receipt and invoice are compared, differences go to approval
- [ ] `[EXT]` Supplier price proposals → the tenant approves (never applied automatically)
- [ ] `[EXT]` Roles and 2FA inside a `SupplierAccount`. ADR: why Django's global Group and Permission system isn't enough here (roles belong to a company); compare with stage 15 and the monolith's RBAC
- [ ] `[OPT]` Messaging on a PO

**Concepts:** cross-tenant identity, security boundary for external users, read model, service-to-service commands and eventual consistency, extending Django auth (custom user model, authentication backend).
**Done when:** one supplier sees two tenants' POs in one place, yet no request can leak one tenant's data to the other (proven by the isolation matrix tests); an attempt to confirm a PO the tenant has cancelled is rejected.

---

## Stage 25: Marketplace sync (FastAPI + worker)
**Where:** `services/marketplace-sync` · **Prerequisites:** 17 and 19

**Why a separate service (ADR):** external marketplace APIs are unreliable, slow and rate limited. Their problems must not affect the monolith, and the service has to scale on its own.

- [ ] `[CORE]` A `MarketplaceAdapter` interface and a **fake marketplace** server (simulates rate limits, 5xx errors, slow responses, duplicate webhooks). Check real APIs (e.g. Uzum Market) against their official docs
- [ ] `[CORE]` Tenant connections and credentials: encrypted storage (envelope encryption), never written to logs
- [ ] `[CORE]` Mapping: variant ↔ marketplace SKU, categories and attributes
- [ ] `[CORE]` Pushing stock: from `stock.changed.v1`, only the latest value per SKU (coalescing, debounce), safety buffer (`available − buffer`)
- [ ] `[CORE]` Pushing prices: a separate price list for the marketplace
- [ ] `[CORE]` **Outbound rate limiting:** token bucket per tenant and marketplace (Redis), batching, `Retry-After` on `429`, circuit breaker
- [ ] `[CORE]` Importing orders: webhook or polling with a cursor; idempotent by marketplace order ID; an order and reservation in the monolith created with `Idempotency-Key` (reusing stage 17)
- [ ] `[CORE]` **Oversell conflict:** the item was already sold at the POS but also sold on the marketplace; policy (cancel or backorder), a conflict record and an alert
- [ ] `[CORE]` Sending order status back to the marketplace (shipped, cancelled), marketplace returns
- [ ] `[CORE]` Reconciliation job: finding and fixing stock and price differences between us and the marketplace
- [ ] `[CORE]` DLQ, sync status dashboard (last sync, errors, lag)
- [ ] `[EXT]` Stock allocation per channel (e.g. only 30% to the marketplace)
- [ ] `[EXT]` Importing marketplace commissions and payouts into finance
- [ ] `[OPT]` A second marketplace adapter

**Concepts:** anti-corruption layer, outbound rate limiting, multi-channel stock, two-way sync, reconciliation.
**Done when:** even with the fake marketplace running at 30% errors and rate limits, stock eventually matches, orders are created without duplicates, and oversell cases end up in the conflict report.

---

# Part II: ERP extension (stages 26–33)

Part I builds a retail SaaS. What separates it from an ERP is that an ERP closes the loop on **money, materials and people**: every document posts to a general ledger, purchasing is driven by a plan instead of by hand, production turns materials into products, payroll turns time into cost, and all of it is reported from one source of truth. Part II adds exactly that.

Rules for part II:
- Start only after the `[CORE]` part of levels 1–3. Nothing here is needed for a job search.
- Every module lives in the **monolith**: each one writes to the same ledgers and stock as sales and must do it in the same transaction. Extraction follows the same conditions as part I.
- Each stage reuses the state machine, ledger, approval and audit machinery of part I. Stage 30 extracts the generic mechanism and migrates the older modules to it.
- The same domain rules apply: `Decimal` money, immutable documents, snapshots, ledgers, state machines, audit, `tenant_id` everywhere.

| Stage | Prerequisites | What it adds |
|---|---|---|
| 26 General ledger and accounting | 8 | Chart of accounts, posting rules, periods, financial statements, multi-currency, bank reconciliation |
| 27 Installment sales, consumer credit and gift cards | 7, 26 | Contracts, schedules, collections, liability ledgers |
| 28 Production | 4, 26 | BOM, work orders, WIP, product cost |
| 29 Demand planning and replenishment | 4, 16 | Forecast, reorder point, suggested POs and transfers |
| 30 Workflow, approvals and document engine | 5, 11 | Generic state machines, configurable approvals, numbering |
| 31 HR and payroll | 11, 26 | Attendance, compensation, payroll runs, payroll accounting |
| 32 Reporting, documents and localization | 23, 26 | Templates, PDF, report engine, exports, i18n |
| 33 Multi-company and intercompany | 26, 30 | Legal entities inside a tenant, intercompany, consolidation |

---

## Stage 26: General ledger and accounting
**Where:** `modules/accounting` · **Prerequisites:** 8

**Why (ADR):** stage 8 reports revenue and profit from sale snapshots. An ERP needs the opposite direction too: every document (sale, receipt, payment, adjustment, payroll) produces balanced journal entries, and every financial report is derived from the ledger, not from the documents. That is what makes the numbers auditable and lets an accountant close a month.

### Chart of accounts and posting
- [ ] `[CORE]` `Account` tree per tenant (code, type: asset / liability / equity / income / expense, currency, active), seeded from a template for the tenant's tax regime; an account with entries can't be deleted
- [ ] `[CORE]` `JournalEntry` and `JournalLine`: debit = credit enforced by a deferred constraint trigger; entries are immutable, mistakes are fixed with a reversing entry (the stage 8 `[EXT]` becomes `[CORE]` here)
- [ ] `[CORE]` **Posting rules as data:** document type × event → accounts (sale: cash or receivable vs revenue and VAT, COGS vs inventory; receipt: inventory vs payable; payment; adjustment; refund). The posting engine is a pure function, like the pricing engine
- [ ] `[CORE]` Posting happens in the **same transaction** as the document; a document that can't post can't complete. ADR: synchronous posting vs posting from events, and why the synchronous side wins for money
- [ ] `[CORE]` Backfill: post every existing part I document; the ledger's revenue must equal the stage 8 report to the tiyin
- [ ] `[CORE]` Sub-ledgers reconcile to the GL: receivables (stage 7), payables (stage 4), inventory value (stage 4 WAC), cash per location (stage 8); a nightly reconciliation job and a differences report

### Periods and reports
- [ ] `[CORE]` Fiscal periods: `open → closing → closed`; posting into a closed period is rejected at the database level; reopening needs a permission and an audit record
- [ ] `[CORE]` Trial balance, general ledger per account, profit and loss, balance sheet; by period, location and cost centre; every report is a `SELECT` over the ledger
- [ ] `[CORE]` Year-end closing: income and expense accounts closed to retained earnings with generated entries
- [ ] `[CORE]` VAT: output and input VAT accounts, a VAT return report for the period (check the current rules for Uzbekistan)
- [ ] `[CORE]` Property-based tests (`hypothesis`): any sequence of documents leaves the trial balance balanced

### Multi-currency, banks and assets
- [ ] `[CORE]` **Multi-currency:** base currency per tenant, exchange rates with validity dates (source plus manual override), amounts stored in document currency and base currency, realised and unrealised FX gain/loss entries
- [ ] `[CORE]` Bank accounts, bank statement import (CSV or MT940-style; ADR on the format), **bank reconciliation:** matching statement lines to payments, suggested matches, unmatched items
- [ ] `[EXT]` Fixed assets: register, depreciation methods (straight-line, declining balance), a monthly depreciation run (Celery beat), disposal
- [ ] `[EXT]` Budgets per account and period, budget vs actual report
- [ ] `[EXT]` Cost centres and analytical dimensions on lines (location, channel, project)
- [ ] `[OPT]` Export to an external accounting system (1C) as journal entries

**Concepts:** double-entry bookkeeping, chart of accounts, posting rules, sub-ledger reconciliation, fiscal periods and closing, multi-currency and FX differences, bank reconciliation.
**Done when:** for any month the trial balance balances, the P&L equals the stage 8 gross profit report, every sub-ledger reconciles to the GL, and a closed period rejects writes even from a raw SQL session without the override role.

---

## Stage 27: Installment sales, consumer credit and gift cards
**Where:** `modules/credit` · **Prerequisites:** 7, 26

**Why (ADR):** in Uzbekistan a large share of electronics, furniture and appliances is sold in instalments (nasiya). Stage 7 has a credit limit and a debt ledger; an ERP needs a contract with a schedule, markup or interest, penalties, collections, and the accounting behind it. Gift cards are the mirror image: money received before goods, a liability tracked per card.

### Installment contracts
- [ ] `[CORE]` `InstallmentContract`: linked to a sale, down payment, term, markup or interest (ADR: markup on price vs interest on balance; rounding so the schedule sums exactly), guarantor, documents (through Media)
- [ ] `[CORE]` Schedule generation: `InstallmentPayment` rows with due dates in the tenant's time zone; the schedule sums to the contract total to the tiyin (largest remainder, as in stage 6)
- [ ] `[CORE]` Contract state machine: `draft → pending_approval → active → completed / defaulted / cancelled`; approval by amount and customer risk; `credit.contract.approve` permission
- [ ] `[CORE]` Repayments: full, partial and early (early repayment recalculates the markup, ADR); allocation order (penalty → markup → principal); payment from the POS, bank or balance; every repayment is a ledger entry and a journal entry
- [ ] `[CORE]` Overdue detection (Celery beat, tenant time zone), penalties as configured, `installment.overdue.v1` → reminders through Notification; escalation steps
- [ ] `[CORE]` Exposure limit per customer: payment history with this tenant, open exposure; new contracts above the limit are blocked with the same account-row lock as stage 7
- [ ] `[CORE]` Collections dashboard: overdue by bucket, location and collector; a customer's full statement
- [ ] `[EXT]` Repossession or return of goods under a defaulted contract: stock movement, write-off entry
- [ ] `[EXT]` Layaway (goods held until fully paid): a reservation with a long TTL plus a schedule
- [ ] `[OPT]` An external BNPL provider behind an adapter (stage 19 pattern)

### Gift cards and vouchers
- [ ] `[CORE]` Gift card as a **liability ledger:** issue (sale of a card is unearned revenue), redeem (a payment method at the POS and online), balance from entries, expiry policy, a breakage entry on expiry
- [ ] `[CORE]` Card codes hashed at rest, activation, blocking; redeem concurrency: two terminals can never spend the same balance twice
- [ ] `[EXT]` Physical vs electronic cards, bulk issue for corporate customers

**Concepts:** amortisation schedule, allocation order, exposure limits, collections, liability ledgers, breakage.
**Done when:** a contract is sold, repaid partially, goes overdue, is penalised and completed, and at every step the customer statement, the credit ledger and the GL agree; two parallel repayments, or two parallel gift-card redemptions, never produce a negative balance.

---

## Stage 28: Production (light manufacturing)
**Where:** `modules/production` · **Prerequisites:** 4, 26

**Why (ADR):** retailers produce: a bakery, a deli counter, a furniture shop assembling sets, a pharmacy compounding. Stage 2's kit assembly is single-level and instantaneous. Production adds a bill of materials with levels, work orders that take time, work-in-progress stock, scrap and a real product cost.

- [ ] `[CORE]` **Bill of materials (BOM):** versioned, multi-level, quantities in `Decimal(12, 3)`, scrap percentage, optional by-products; cycle detection in the BOM graph
- [ ] `[CORE]` `WorkOrder` state machine: `draft → planned → released → in_progress → completed / cancelled`; partial completion
- [ ] `[CORE]` Material consumption: reservation on release, `production_consume` movements on start or on completion (ADR: backflush vs manual issue); FEFO for batches
- [ ] `[CORE]` Output: a `production_output` movement into stock with a new batch; by-products; scrap as a separate movement with a reason
- [ ] `[CORE]` **Work-in-progress:** a WIP account in the GL; consumption posts to WIP, completion posts from WIP to inventory; product cost is materials plus allocated labour and overhead (rate per hour, ADR); variance vs the BOM standard cost reported
- [ ] `[CORE]` Availability check before release ("can I make 50 cakes today?"); the shortage report feeds stage 29
- [ ] `[EXT]` Routing and operations (steps, work centres, durations); a capacity view per work centre
- [ ] `[EXT]` Disassembly (a reverse work order)
- [ ] `[OPT]` Production planning from the sales forecast (stage 29); recipes with yield by weight

**Concepts:** BOM explosion, WIP accounting, backflushing, standard vs actual cost, by-products and scrap.
**Done when:** a multi-level BOM is produced end to end; components, WIP, finished stock and the GL agree; the finished product's cost equals materials plus overhead, and the stage 3 reconciliation still passes.

---

## Stage 29: Demand planning and replenishment (MRP-lite)
**Where:** `modules/planning` · **Prerequisites:** 4, 16

**Why (ADR):** part I reorders when stock falls below a hand-set minimum. An ERP computes what to buy from forecast demand, lead times and what is already on order, across locations. This module turns inventory from a record into a plan.

- [ ] `[CORE]` Demand forecast per variant and location from the Analytics read models (moving average, exponential smoothing, a weekday profile for seasonality); ADR: where the computation runs and how the result returns to the core as data
- [ ] `[CORE]` Replenishment parameters: lead time per supplier and variant, safety stock, review period, minimum order quantity, pack size, maximum stock
- [ ] `[CORE]` **Reorder point and order quantity:** `reorder_point = demand × lead_time + safety_stock`; projected stock = on hand − reserved + on order (open POs and transfers) − forecast; a suggestion when projected stock crosses the reorder point
- [ ] `[CORE]` Suggested purchase orders grouped by supplier, respecting MOQ and pack size; one click creates draft POs (stage 4); `replenishment.suggested.v1`
- [ ] `[CORE]` Multi-location: transfer suggestions from a location with excess to one with shortage before buying
- [ ] `[CORE]` The planning run is a Celery beat job per tenant under a distributed lock; the result is a snapshot with a run ID, so two runs never mix
- [ ] `[CORE]` Exception report: stock-outs, overstock, dead stock, forecast error (MAPE) per product
- [ ] `[EXT]` Promotion-aware forecast (the stage 6 calendar lifts demand)
- [ ] `[EXT]` Open-to-buy budget per category and period
- [ ] `[OPT]` Suggested POs visible to the supplier as a forecast (stage 24)

**Concepts:** forecasting basics, reorder point, safety stock, projected inventory, exception-based management.
**Done when:** on seeded history the planning run proposes POs that would have avoided the seed's stock-outs, and never proposes buying what is already on order.

---

## Stage 30: Workflow, approvals and document engine
**Where:** `modules/workflow` · **Prerequisites:** 5, 11

**Why (ADR):** by now the project has eight state machines and four approval flows, each written by hand. An ERP lets the tenant configure approvals and numbering without code. This stage extracts the common mechanism and migrates the old modules to it. It is also the biggest refactoring exercise in the project.

- [ ] `[CORE]` A generic **state machine framework:** states, transitions, guards and effects declared per document type; `transition()` logs every change with actor, reason and correlation ID; a test forbids direct status writes
- [ ] `[CORE]` Migrate the existing machines (sale, PO, transfer, order, contract, work order) to it, one PR each, behaviour unchanged (**characterisation tests** first)
- [ ] `[CORE]` **Approval workflows as data:** steps, approver by role or user, thresholds by amount or percentage, parallel vs sequential, delegation while on leave, escalation by timeout (Celery beat); the stage 5 step-up PIN becomes one step type
- [ ] `[CORE]` Document numbering: configurable sequences per document type and location (prefix, yearly reset); gapless where required (the stage 5 counter row) and not where not (ADR on the cost)
- [ ] `[CORE]` Inbox: "documents waiting for me", with notifications through the Notification service
- [ ] `[CORE]` Workflow configuration is a sensitive operation; changing a workflow never affects documents already in flight (the version is pinned on the document)
- [ ] `[EXT]` Reminders and SLA timers per step; a report of approval lead times
- [ ] `[OPT]` A visual workflow editor in the back-office (HTMX)

**Concepts:** generic state machines, configuration over code, refactoring under test, characterisation tests, versioned configuration.
**Done when:** every document type in the project runs on the framework, every old test still passes, and a tenant adds a second approval step to purchase orders above an amount without a deploy.

---

## Stage 31: HR and payroll
**Where:** `modules/hr`, `modules/payroll` · **Prerequisites:** 11, 26

**Why (ADR):** stage 11 was deliberately minimal. An ERP pays people: schedules and attendance become hours, hours and sales become pay, pay becomes journal entries and tax reports. Payroll rules change with the law, so the calculation must be data-driven and versioned.

- [ ] `[CORE]` Work schedules and attendance become `[CORE]`: shifts per location, check-in and check-out from the POS (linked to the cash shift), overtime and absence types, leave balances as a ledger
- [ ] `[CORE]` Compensation: salary, hourly, commission from sales (from sale snapshots, by cashier), bonuses; effective-dated changes
- [ ] `[CORE]` **Payroll run** per period: `draft → calculated → approved → paid → posted`; the calculation is a pure function over versioned rule sets (income tax, social contributions; check the current Uzbek rules and keep them as data with validity dates); recalculation is idempotent
- [ ] `[CORE]` Payslips (PDF through stage 32), payment through finance (stage 8) and a bank export file; `payroll.posted.v1`
- [ ] `[CORE]` Journal entries: salary expense, taxes payable, net pay payable; posted to the GL in the same transaction as approval
- [ ] `[CORE]` Privacy: salary data behind a separate permission, masked in logs, never in analytics events in raw form
- [ ] `[EXT]` Cashier KPIs feed bonuses; shortage deductions from cash differences (stage 5) by policy
- [ ] `[EXT]` Employee self-service: payslips, leave requests through the approval engine (stage 30)
- [ ] `[OPT]` Extraction into a Django service (the stage 11 `[OPT]`), now with real scope

**Concepts:** effective dating, versioned rule sets, payroll accounting, privacy by permission.
**Done when:** a payroll run for a month with overtime, commission and leave produces payslips, a bank file and balanced journal entries; rerunning the calculation gives identical results.

---

## Stage 32: Reporting, documents and localization
**Where:** `modules/reporting`, `modules/documents` · **Prerequisites:** 23, 26

**Why (ADR):** an ERP's output is documents and reports: invoices, contracts, payslips, statements, and reports an accountant can schedule and export. Each tenant needs them in its own language, format and layout.

### Documents
- [ ] `[CORE]` Document templates per tenant and type (receipt, invoice, PO, contract, payslip, statement): Jinja2 templates with a versioned schema of variables; a rendered document is stored as a snapshot in Media and never re-rendered
- [ ] `[CORE]` PDF rendering in a worker (library by ADR; fonts for Latin and Cyrillic), barcodes and QR codes on documents
- [ ] `[CORE]` Numbering and verification: document number from stage 30; an optional signature or hash printed on the document for verification
- [ ] `[EXT]` Delivery of documents by email and Telegram through Notification, with Media links

### Reporting engine
- [ ] `[CORE]` Report definitions as data: parameters (period, location, dimensions), a whitelisted query or a read-model source, output columns; large reports run asynchronously with progress (the stage 9 pattern)
- [ ] `[CORE]` Scheduled reports (Celery beat, tenant time zone) delivered as files through Media and Notification
- [ ] `[CORE]` Exports: CSV, XLSX and a format for 1C; streaming for large results, never loading everything into memory
- [ ] `[CORE]` Row-level security on reports: a branch manager sees only their locations, finance sees all; the same permission layer as the API
- [ ] `[EXT]` A data export API for BI tools (cursor pagination, incremental `updated_since`)
- [ ] `[OPT]` Pivot-style ad-hoc reports in the back-office

### Localization
- [ ] `[CORE]` Interface locales uz-Latn, uz-Cyrl and ru (gettext or a catalogue; ADR); number, date and currency formatting per tenant; documents and notifications in the customer's locale
- [ ] `[CORE]` Multi-language catalog: product names and descriptions per locale with fallback; search works across locales (stage 10 transliteration)
- [ ] `[EXT]` Tenant-specific tax and receipt format rules as configuration (started in stage 1), not code

**Concepts:** templating with versioned contracts, asynchronous report execution, streaming exports, i18n and l10n.
**Done when:** an invoice, a payslip and a statement render in all three locales from templates a tenant customised; a scheduled report for the largest tenant runs without memory growth and arrives by Telegram.

---

## Stage 33: Multi-company and intercompany
**Where:** `modules/accounting`, `modules/inventory` · **Prerequisites:** 26, 30

**Why (ADR):** a tenant is a business, but a business can be several legal entities: a chain with one company per region, a franchise, a group with a wholesale arm and a retail arm. Each entity has its own books and VAT, yet they share a catalog, customers and staff. This is the last step from "shop software" to "ERP".

- [ ] `[CORE]` `Company` inside a tenant: legal entity details, base currency, its own chart of accounts (from the tenant template), fiscal calendar; every location belongs to one company; every document and journal entry carries `company_id`
- [ ] `[CORE]` Permissions and reports are company-aware; a user may have access to several companies; `404` across companies within a tenant, the same fail-closed pattern as for tenants
- [ ] `[CORE]` **Intercompany transfer:** a transfer between locations of different companies becomes a sale in one and a receipt in the other at a transfer price, with mirrored journal entries and intercompany receivable and payable accounts; both documents in one transaction
- [ ] `[CORE]` Consolidation: group reports that eliminate intercompany balances; by period and currency
- [ ] `[EXT]` Franchise mode: a franchisee company sees only its own books, the franchisor sees all and charges royalties as generated invoices
- [ ] `[OPT]` Separate Postgres schemas or databases per company (ADR: when tenant-level RLS is not enough; the cost of a second isolation axis)

**Concepts:** legal entity vs business unit, intercompany accounting, consolidation and elimination, a second isolation axis.
**Done when:** a transfer between two companies of one tenant produces matching entries on both sides, the consolidated report eliminates them, and each company's trial balance still balances on its own.

---

# Conditions for extracting a microservice

Before extracting any module, **all** of these must be true:

- [ ] Data ownership is clear: other modules never access the module's tables directly, no JOINs
- [ ] Communication only through interfaces or events, enforced by `import-linter`
- [ ] The outbox works, events are versioned
- [ ] Correlation IDs are in every log
- [ ] CI can build several images
- [ ] The concrete reason for extraction is written in an ADR

---

# Theory tracks (in parallel with the stages)

## Python internals
**When:** during stages 1–9. **Source:** *Fluent Python* (Luciano Ramalho)

- [ ] Decorators and closures (how `Depends`, `@router.get` and `@task` work)
- [ ] Context managers and `contextvars` (Unit of Work, tenant context)
- [ ] Iterables, iterators, generators; list, dict and set comprehensions; generator-based streaming for exports
- [ ] Mutable default arguments, duck typing, EAFP vs LBYL, MRO and `super()`, dunder methods
- [ ] Dataclass vs Pydantic model vs SQLAlchemy model: which one where in this project, and why
- [ ] Descriptors (how SQLAlchemy columns and Pydantic fields work)
- [ ] Metaclasses and `__init_subclass__` (how SQLAlchemy declarative and Pydantic models are created)
- [ ] The GIL: threads vs processes vs asyncio; I/O-bound vs CPU-bound; concurrency vs parallelism; `run_in_executor` and a process pool for image processing (stage 23)
- [ ] asyncio: event loop, coroutines, tasks, blocking calls, cancellation (**from stage 0**, the project is async)
- [ ] Memory management: reference counting, the cyclic garbage collector, circular references, `tracemalloc`
- [ ] Typing: generics, Protocol, `TypedDict`, mypy strict vs pyright; monkey patching, and why `patch` is a smell when a fake exists
- [ ] Packaging: venv, uv vs poetry and pipenv (the stage 0 choice), lock files, wheel vs sdist, building the app as a wheel inside the Docker image

## PostgreSQL internals
**When:** during stages 3–10

- [ ] MVCC: row versions, snapshots
- [ ] Isolation levels in Postgres: snapshot isolation, serializable snapshot isolation (SSI), which anomalies each level allows (the stage 5 lab)
- [ ] Lock types: row, table, advisory; `pg_locks`, `pg_stat_activity`; deadlock detection
- [ ] The planner: statistics, `ANALYZE`, join strategies (nested loop, hash, merge), why an index gets ignored
- [ ] Normal forms, and when to denormalize on purpose
- [ ] VACUUM, autovacuum, bloat
- [ ] WAL and checkpoints (what durability actually costs)
- [ ] Replication: streaming and logical; read replicas and lag; failover

## System design at scale
**When:** from stage 10. **Source:** *Designing Data-Intensive Applications* (Martin Kleppmann)

- [ ] Storage engines (B-tree vs LSM-tree)
- [ ] Replication and consistency models: strong vs eventual, read-your-writes
- [ ] Sharding and consistent hashing; hotspots and hot keys
- [ ] CAP theorem, partition tolerance and PACELC
- [ ] Consensus and leader election (Raft; Kafka KRaft; a Kubernetes lease)
- [ ] High availability: single points of failure, failover, load balancers, stateless vs stateful services
- [ ] Flow control: backpressure, thundering herd, bulkheads, graceful degradation
- [ ] Stream processing
- [ ] CDN and multi-region architecture
- [ ] Paper design exercises: URL shortener, chat, taxi service
- [ ] Design doc: "How does my project work with 100× more tenants?"

## Software design
**When:** from stage 2, revisited at stages 13 and 30. **Source:** *Architecture Patterns with Python* (Percival, Gregory)

- [ ] Service layer, repository pattern, Unit of Work: what each one isolates and what it costs (the stage 0 ADR)
- [ ] Dependency injection and inversion of control: FastAPI `Depends` vs a container; why the pricing engine takes its rules as arguments
- [ ] SOLID with one example from this project per principle: SRP (sale completion vs receipt rendering), OCP (a new promotion type without touching the engine), LSP (every `PaymentProvider` fake passes the same contract test), ISP (small adapter interfaces in stage 19), DIP (modules depend on interfaces, enforced by `import-linter`)
- [ ] DRY, KISS, YAGNI and their limits: when duplication is cheaper than the wrong abstraction
- [ ] Coupling and cohesion, separation of concerns; module boundaries and bounded contexts (stage 13)
- [ ] Code smells, technical debt, boilerplate; refactoring under tests (stage 30 is the big one)
- [ ] Domain model: entities, value objects (`Money`), aggregates (a sale and its lines); invariants kept in one transaction
- [ ] Hexagonal architecture, ports and adapters, clean architecture: how the stage 19 adapters and the pure engines fit; what this project deliberately doesn't do
- [ ] CQRS (the stage 16 read models) and event sourcing: an ADR on why the ledgers are append-only but the project is not event-sourced

## Web and API design
**When:** stages 0, 1, 9, 17

- [ ] Request lifecycle: ASGI, middleware order, dependencies, exception handlers, response serialization
- [ ] REST vs RPC vs GraphQL: resource design, status codes, error format; when a command endpoint beats a resource
- [ ] Serialization and validation: Pydantic v2 (strict mode, `Decimal`), DRF serializers
- [ ] Versioning, backward compatibility, breaking changes: a URL version for the API, a schema version for events
- [ ] Rate limiting vs throttling: fixed window, sliding window, token bucket; where to enforce (edge, app, outbound)
- [ ] Push options: polling, long polling, SSE, WebSocket, webhooks; chosen per use case in stages 9, 17, 18, 19
- [ ] CORS and preflight; cookies vs bearer tokens and what that changes for CSRF

## Testing
**When:** from stage 0

- [ ] The test pyramid: unit (the pure engines of stages 6, 26, 31), integration (Testcontainers, real Postgres and Redis), end-to-end (Playwright, stage 18), smoke and synthetic checks (stage 20), a regression test for every bug
- [ ] Test doubles: fake (an in-memory adapter), stub (fixed answers), mock and spy (assert calls), `patch`; when each one is right, and why fakes for ports are the default here
- [ ] Fixtures: scope, factories (factory_boy in Django, your own in FastAPI), transaction rollback per test, `dependency_overrides`
- [ ] Coverage as a signal, not a target; mutation testing `[OPT]`
- [ ] Flaky tests: time, ordering, shared state, real clocks; freezing time and seeded randomness
- [ ] Contract tests (Pact) between services; property-based tests (`hypothesis`)
- [ ] Load, stress and soak tests (Locust); benchmarks with before/after numbers in the README

## Security
**When:** stage 1, then every stage that adds an entry point. **Source:** OWASP Top 10, OWASP ASVS

- [ ] Authentication vs authorization; sessions vs tokens; access and refresh tokens, rotation and reuse detection
- [ ] RBAC vs ABAC; least privilege for users, service tokens and database roles
- [ ] OAuth 2.0 and OIDC: flows, when to integrate an identity provider; JWT pitfalls (`alg`, audience, clock skew), JWKS rotation
- [ ] Password and secret hashing: Argon2, salting, pepper; OTP and PIN hashing with attempt limits
- [ ] Injection (SQL, command), XSS and CSP, CSRF, SSRF, open redirects, mass assignment; one test per class of attack in the project
- [ ] Secret management and rotation; encryption at rest (envelope encryption, stage 25); PII in logs
- [ ] Threat modelling of one flow (refund) and one boundary (supplier portal)

## Django and ORM
**When:** stages 15, 22, 24

- [ ] Django ORM vs SQLAlchemy: `QuerySet` laziness, `select_related` (JOIN) vs `prefetch_related` (second query) vs `selectinload` / `joinedload`; the N+1 helper works in both
- [ ] `annotate`, `aggregate`, `F` and `Q` expressions, `Subquery`; raw SQL and `RunSQL` migrations
- [ ] Migrations: Django `makemigrations` / `migrate` vs Alembic autogenerate; expand/contract in both
- [ ] Signals: what they are, and why this project puts side effects in the service layer instead
- [ ] WSGI vs ASGI for Django; where sync is fine (stages 15, 22, 24)
- [ ] DRF: serializers, ViewSets, permission classes, throttling, pagination; the ADR comparing them with Pydantic and FastAPI dependencies

## Networking and Linux
**When:** throughout the project, especially in stages 0, 12, 18 and 21

- [ ] TCP: handshake, retransmission, keep-alive
- [ ] How DNS works
- [ ] TLS handshake and certificates
- [ ] Differences between HTTP/1.1, HTTP/2 and HTTP/3; the WebSocket protocol
- [ ] Processes, threads, signals
- [ ] Containers from the inside: namespaces, cgroups
- [ ] Debugging: `ps`, `top`, `ss`, `lsof`, `strace`, `tcpdump`, `curl -v`

## Algorithms
**When:** from the start, regularly. **Level:** medium

- [ ] Arrays, hash maps, two pointers, sliding window
- [ ] Stacks, queues, heaps
- [ ] Binary search
- [ ] Trees, BFS and DFS
- [ ] Graph basics
- [ ] Dynamic programming basics

---

# Team and production experience

- [ ] After the level 1 MVP (0, 1, 2, 3, 5, 9, 10): resume, job applications
- [ ] At least 3 PRs to open source
- [ ] A postmortem for every chaos experiment
- [ ] A "decision story" for every technology: why, the alternative, the cost
- [ ] Mock interviews: coding and system design
- [ ] 3–5 technical articles: deadlocks, multi-tenancy with RLS, the promotions engine, offline sync, the outbox pattern
- [ ] Code review vocabulary in practice: `nit:` vs `blocker:` prefixes, LGTM only after running the code; a review checklist in `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] An **RFC** (request for comments) in `docs/rfc/` before every big change; the first one: Kafka vs RabbitMQ for domain events (stage 13)
- [ ] A time-boxed **spike** (proof of concept) before every unfamiliar technology (ClickHouse, PostGIS, PWA); the result is a decision, the code is thrown away
- [ ] Every PR description names the happy path, the edge cases, the fallback, the trade-offs and the **blast radius** of the change
- [ ] Postmortems find the root cause with "5 whys"; action items are tracked to completion

---

# Concept index

Every term an interviewer may ask, mapped to where this roadmap teaches it. A stage number means the task where the concept is used for real; "track" means a theory track above. Tick a term only when you can explain it with an example **from this project**: why, the alternative, and the cost.

## 1. Database and SQL

| Term | Where |
|---|---|
| ACID: atomicity, consistency, isolation, durability; transaction, commit, rollback, savepoint | Stage 5 (completion, ACID lab), stage 0 Unit of Work; PostgreSQL track (WAL) |
| N+1 query problem, lazy loading, eager loading (`selectinload`, `joinedload`) | Stage 10; Django track (`select_related`, `prefetch_related`) |
| Join: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN; semi and anti joins | Stage 10 SQL lab; PostgreSQL track (join strategies) |
| Index, composite index, covering index, partial, BRIN, GIN; full table scan; query plan, execution plan | Stage 2 (sub-10 ms lookup), stage 10 `EXPLAIN` |
| Normalization, denormalization | Stage 10 summary tables; PostgreSQL track |
| Primary key, foreign key, unique constraint, `CHECK` | Stages 1–3 models; stage 13 (removing cross-module FKs) |
| Upsert | Stage 9 import |
| Locking: pessimistic, optimistic; deadlock; race condition; lost update | Stage 3 reservations, stage 5 concurrency lab, stage 7 credit limit |
| Isolation levels: read uncommitted, read committed, repeatable read, serializable; dirty, non-repeatable and phantom reads | Stage 5 isolation lab; PostgreSQL track (MVCC, SSI) |
| Replication, read replica | Stage 10 `[EXT]`, stage 21 failover; PostgreSQL track |
| Sharding, partitioning | Stage 10 (table partitioning), stage 13 (Kafka partitions); system design track (sharding) |
| Materialized view | Stage 10, stage 16 (ClickHouse) |
| Cursor pagination vs offset pagination | Stage 3 movement history, stage 10 |
| Connection pool | Stage 10 (PgBouncer, SQLAlchemy pool) |

## 2. Distributed systems and backend

| Term | Where |
|---|---|
| Idempotency, idempotency key | Stages 5, 12, 14, 17, 25 |
| Retry, exponential backoff (and jitter), timeout | Stage 9 Celery, stage 14, stage 19 adapters |
| Circuit breaker, bulkhead, graceful degradation | Stage 19, stage 25 |
| At-most-once, at-least-once, exactly-once semantics | Stage 13 ADR, stage 14 consumer, stage 16 projections |
| Eventual consistency, strong consistency | Architecture "what lives where", stage 12 offline, stage 15 tenant replica |
| CAP theorem, partition tolerance, PACELC | System design track |
| SLA, SLO, SLI, error budget | Stage 20 |
| Backpressure, thundering herd, hotspot, hot key | Stage 9 (prefetch, stampede), stage 10 hotspots; system design track |
| Single point of failure (SPOF), high availability, failover | Stage 21 HA |
| Leader election, consensus | Stage 21 singletons, stage 9 distributed lock; system design track (Raft, KRaft) |

## 3. API and web

| Term | Where |
|---|---|
| REST, RPC, GraphQL, CRUD, endpoint | Stage 1 API standards, stage 17 ADR; web and API track |
| Serialization, deserialization, schema, validation | Stage 0 Pydantic, stage 13 event schemas, stage 15 DRF serializers |
| Rate limiting vs throttling | Stage 1 (sliding window), stage 15 (DRF throttling), stage 25 (token bucket) |
| Pagination, filtering, sorting | Stage 10 |
| Versioning, backward compatibility, breaking change | Stage 1 `/api/v1/`, stage 13 event versions, stage 17 public API |
| Webhook, polling, long polling, WebSocket, SSE (server-sent events) | Stage 9 `[EXT]`, stages 15 and 17 (payment webhooks), stage 18 (tracking), stage 19 (outbound webhooks) |
| CORS, preflight request | Stage 0 middleware, stage 17 storefront |
| Middleware, request lifecycle | Stage 0, stage 1 tenant middleware; web and API track |

## 4. Caching

| Term | Where |
|---|---|
| Cache hit, cache miss, TTL (time to live), cache invalidation | Stage 9 |
| Cache-aside, write-through, write-back | Stage 9 ADR |
| Cache stampede, warm-up, eviction policy, LRU, LFU | Stage 9 |
| HTTP caching (`ETag`, `Cache-Control`), CDN | Stage 17, stage 23 |

## 5. Message brokers and queues

| Term | Where |
|---|---|
| Message queue vs event stream, broker, producer, consumer | Stage 9 (RabbitMQ), stage 13 (Kafka); architecture notes ("RabbitMQ carries work, Kafka carries facts") |
| Pub/sub, topic, partition, offset, consumer group, ordering | Stage 13, stage 16 (offset commit, replay), stage 9 (Redis pub/sub) |
| Ack (acknowledgement), requeue, dead letter queue (DLQ), poison message | Stage 9 Celery, stage 14 Notification |
| Outbox pattern, inbox pattern | Stage 13 |
| Saga pattern: orchestration vs choreography | Stage 15 (provisioning), stage 18 (failed delivery) |

## 6. Architecture and design

| Term | Where |
|---|---|
| Monolith, modular monolith, microservice | Stage 0 ADR, stage 13, "Conditions for extracting a microservice" |
| Service layer, repository pattern, Unit of Work | Stage 0; software design track |
| Dependency injection (DI), inversion of control (IoC) | Stage 0 (`Depends`), stage 1 permissions; software design track |
| SOLID: single responsibility, open/closed, Liskov substitution, interface segregation, dependency inversion | Software design track, with an example from stages 6 and 19 per principle |
| DRY, KISS, YAGNI, separation of concerns | Software design track |
| Coupling, cohesion, code smell, technical debt, refactoring, boilerplate | Stage 13 (`import-linter`), stage 30 (refactoring under test); software design track |
| Domain model, bounded context | Stage 13 module boundaries; software design track |
| CQRS, event sourcing | Stage 16 read models; software design track (ADR on why not event sourcing) |
| Hexagonal architecture, ports and adapters, clean architecture | Stage 19 adapters; software design track |

## 7. Python

| Term | Where |
|---|---|
| GIL (global interpreter lock), threading, multiprocessing, concurrency vs parallelism, I/O-bound vs CPU-bound | Python track; stage 9 (sync workers), stage 23 (image processing) |
| async, await, coroutine, event loop | Stage 0 onwards; Python track |
| Context manager, decorator, closure, generator, iterator, iterable, list comprehension, dict comprehension, set comprehension | Python track; stage 0 Unit of Work, stage 1 permission dependencies |
| Mutable default argument, duck typing, EAFP vs LBYL, MRO (method resolution order), dunder methods | Python track |
| Dataclass, Pydantic, type hinting, static typing, mypy, pyright, Protocol | Stage 0 (mypy strict); Python track |
| Monkey patching, descriptor, metaclass | Python track |
| Garbage collection (GC), reference counting, circular reference | Python track; stage 10 profiling |
| Virtual environment (venv), uv vs poetry and pipenv, wheel, source distribution (sdist) | Stage 0; Python track |

## 8. Django, ORM and web frameworks

| Term | Where |
|---|---|
| ORM (object-relational mapping), migration | Stage 0 (SQLAlchemy, Alembic), stage 15 (Django ORM), stage 22 (`RunSQL`) |
| QuerySet, `select_related`, `prefetch_related`, annotation, aggregation | Stages 15, 22, 24; Django track (compared with SQLAlchemy) |
| Signal | Django track (why this project avoids them) |
| ASGI, WSGI | Stage 0 ADR; Django track |
| Dependency override, serialization layer | Stage 0 tests; stage 15 ADR (DRF serializers vs Pydantic) |

## 9. Testing

| Term | Where |
|---|---|
| Unit test, integration test, end-to-end test (E2E), smoke test, regression test | Stage 0 pyramid, stage 18 (Playwright), stage 20 (synthetic checks); testing track |
| Fixture, mock, stub, fake, spy, patch | Stage 0, stage 19 fakes; testing track |
| Test coverage, flaky test | Stage 0 CI; testing track |
| Contract test | Stages 16, 18, 24 (Pact) |
| Load test, stress test, benchmark | Stage 5 (Locust), stage 10 (before/after) |
| Property-based test | Stages 6, 26, 31 |

## 10. Observability and production

| Term | Where |
|---|---|
| Logging, structured logging | Stage 13 (structlog), stage 20 |
| Metrics, tracing, distributed tracing, correlation ID | Stage 13, stage 20 |
| Latency, throughput, P95, P99, tail latency | Stage 20 |
| Error budget, alert fatigue | Stage 20 |
| Health check, liveness probe, readiness probe | Stage 0, stage 21 |

## 11. DevOps and deployment

| Term | Where |
|---|---|
| CI (continuous integration), CD (continuous delivery vs continuous deployment), build, artifact | Stage 0, stage 21 |
| Docker, container, image | Stage 0 |
| Orchestration, Kubernetes | Stage 21 |
| Blue-green, canary, rolling deployment, rollback | Stage 21 |
| Infrastructure as Code (IaC), immutable infrastructure, secret management | Stage 21 |

## 12. Security

| Term | Where |
|---|---|
| Authentication vs authorization | Stage 1 |
| RBAC (role-based access control), ABAC (attribute-based access control) | Stage 1, stage 15 (Django groups), stage 24 |
| OAuth 2.0, JWT, access token, refresh token, session | Stage 1, stage 15 (JWKS, impersonation); security track |
| Hashing, salting | Stage 1 (Argon2, OTP, PIN) |
| SQL injection, XSS, CSRF, SSRF, CSP (content security policy) | Stage 1 baseline, stage 19 (SSRF on outbound calls) |
| Least privilege, secret rotation | Stage 1 DB roles, stage 21, stage 22 (append-only role) |

## 13. Performance and reliability

| Term | Where |
|---|---|
| Bottleneck, profiling, memory leak | Stage 10 |
| Cold start, warm path, hot path, critical path | Stage 5 (sale completion is the hot and critical path), stage 9 (cache warm-up), stage 21 (pod start, readiness) |
| Tail latency | Stage 20 |
| Horizontal scaling, vertical scaling, autoscaling, load balancer | Stage 21 |
| Sticky session, stateless, stateful | Stage 1 (sessions in Redis), stage 21 |

## 14. Code review and team communication

| Term | Where |
|---|---|
| LGTM, nit, blocker | Team section (review checklist) |
| RFC (request for comments), PoC (proof of concept), spike, MVP (minimal viable product) | Team section; MVP line; RFC template |
| Edge case, happy path, fallback, trade-off, blast radius | Team section (PR description); every ADR's "Consequences" |
| Root cause, postmortem | Stage 20; postmortem template |

---

# Templates

## ADR template (`docs/adr/NNNN-name.md`)

```markdown
# NNNN. Decision title

**Status:** proposed / accepted / rejected
**Date:** YYYY-MM-DD

## Context
What is the problem? What constraints exist?

## Decision
What did we decide to do?

## Alternatives considered
Each one, and why it wasn't chosen.

## Consequences
What gets better, what gets more expensive, what needs to be watched?
```

## Postmortem template (`docs/postmortems/YYYY-MM-DD-name.md`)

```markdown
# Postmortem: short name

## Summary
What happened and what was the impact?

## Timeline
When it started, when it was detected, when it was fixed.

## Root cause
Using the "5 whys" method.

## How it was detected
Which alert, log or trace helped? What was missing?

## Fix
Temporary and permanent solutions.

## Action items
- [ ] What will be done so it doesn't happen again
```

## RFC template (`docs/rfc/NNNN-name.md`)

```markdown
# RFC NNNN: title

**Status:** draft / in review / accepted / rejected
**Author and date:**

## Problem
What hurts today, with evidence (numbers, incidents, a failing test).

## Proposal
What changes, in enough detail to review. Happy path, edge cases, fallback.

## Alternatives
Each one with its trade-offs.

## Blast radius and rollout
What can break, how it rolls out, how it rolls back.

## Open questions
```
