# Theory tracks

One task per topic. Done when you can explain the topic with an example from this project (write 5–10 lines in `docs/notes/<track>.md`).

## Python internals (stages 1–9, Fluent Python)

- [ ] **TH.PY01** Decorators and closures → explain `Depends`, `@router.get`, `@task`
- [ ] **TH.PY02** Context managers and `contextvars` → UoW, tenant context
- [ ] **TH.PY03** Iterables, iterators, generators, comprehensions → streaming export
- [ ] **TH.PY04** Mutable default args, duck typing, EAFP vs LBYL, MRO, dunder methods
- [ ] **TH.PY05** Dataclass vs Pydantic vs SQLAlchemy model: which where
- [ ] **TH.PY06** Descriptors → how SQLAlchemy columns and Pydantic fields work
- [ ] **TH.PY07** Metaclasses and `__init_subclass__` → declarative models
- [ ] **TH.PY08** GIL, threads vs processes vs asyncio, I/O- vs CPU-bound, `run_in_executor`
- [ ] **TH.PY09** asyncio: event loop, tasks, cancellation, blocking calls
- [ ] **TH.PY10** Memory: refcount, cyclic GC, circular refs, `tracemalloc`
- [ ] **TH.PY11** Typing: generics, Protocol, TypedDict, mypy vs pyright; monkey patching
- [ ] **TH.PY12** Packaging: venv, uv vs poetry/pipenv, lock files, wheel vs sdist

## PostgreSQL internals (stages 3–10)

- [ ] **TH.PG01** MVCC: row versions, snapshots
- [ ] **TH.PG02** Isolation levels, SSI, anomalies per level
- [ ] **TH.PG03** Locks: row, table, advisory; `pg_locks`, deadlock detection
- [ ] **TH.PG04** Planner: statistics, join strategies, ignored indexes
- [ ] **TH.PG05** Normal forms and deliberate denormalization
- [ ] **TH.PG06** VACUUM, autovacuum, bloat
- [ ] **TH.PG07** WAL and checkpoints
- [ ] **TH.PG08** Replication: streaming, logical, lag, failover

## System design at scale (from stage 10, DDIA)

- [ ] **TH.SD01** B-tree vs LSM-tree
- [ ] **TH.SD02** Consistency models: strong, eventual, read-your-writes
- [ ] **TH.SD03** Sharding, consistent hashing, hotspots
- [ ] **TH.SD04** CAP, partition tolerance, PACELC
- [ ] **TH.SD05** Consensus and leader election (Raft, KRaft, leases)
- [ ] **TH.SD06** HA: SPOF, failover, load balancers, stateless vs stateful
- [ ] **TH.SD07** Backpressure, thundering herd, bulkhead, graceful degradation
- [ ] **TH.SD08** Stream processing
- [ ] **TH.SD09** CDN and multi-region
- [ ] **TH.SD10** Paper designs: URL shortener, chat, taxi
- [ ] **TH.SD11** Design doc: 100× more tenants

## Software design (from stage 2; Architecture Patterns with Python)

- [ ] **TH.SW01** Service layer, repository, UoW: what each isolates and costs
- [ ] **TH.SW02** DI and IoC: `Depends` vs container
- [ ] **TH.SW03** SOLID with one project example per principle
- [ ] **TH.SW04** DRY, KISS, YAGNI and their limits
- [ ] **TH.SW05** Coupling, cohesion, separation of concerns, bounded contexts
- [ ] **TH.SW06** Code smells, technical debt, boilerplate, refactoring under tests
- [ ] **TH.SW07** Domain model: entities, value objects, aggregates, invariants
- [ ] **TH.SW08** Hexagonal / ports and adapters / clean architecture
- [ ] **TH.SW09** CQRS and event sourcing: why not event-sourced (ADR)

## Web and API design (stages 0, 1, 9, 17)

- [ ] **TH.WEB01** Request lifecycle: ASGI, middleware, dependencies, handlers
- [ ] **TH.WEB02** REST vs RPC vs GraphQL; status codes; error format
- [ ] **TH.WEB03** Serialization/validation: Pydantic v2, DRF serializers
- [ ] **TH.WEB04** Versioning, backward compatibility, breaking changes
- [ ] **TH.WEB05** Rate limiting vs throttling: algorithms and placement
- [ ] **TH.WEB06** Polling, long polling, SSE, WebSocket, webhooks
- [ ] **TH.WEB07** CORS and preflight; cookies vs bearer tokens and CSRF

## Testing (from stage 0)

- [ ] **TH.TS01** Test pyramid: unit, integration, e2e, smoke, regression
- [ ] **TH.TS02** Test doubles: fake, stub, mock, spy, patch
- [ ] **TH.TS03** Fixtures: scope, factories, rollback per test, dependency overrides
- [ ] **TH.TS04** Coverage as a signal; mutation testing
- [ ] **TH.TS05** Flaky tests: time, ordering, shared state
- [ ] **TH.TS06** Contract tests (Pact), property-based tests (hypothesis)
- [ ] **TH.TS07** Load, stress, soak tests; benchmarks

## Security (stage 1 onward; OWASP)

- [ ] **TH.SEC01** AuthN vs AuthZ; sessions vs tokens; refresh rotation
- [ ] **TH.SEC02** RBAC vs ABAC; least privilege
- [ ] **TH.SEC03** OAuth 2.0 / OIDC; JWT pitfalls; JWKS rotation
- [ ] **TH.SEC04** Hashing: Argon2, salt, pepper; OTP/PIN limits
- [ ] **TH.SEC05** Injection, XSS/CSP, CSRF, SSRF, open redirect, mass assignment
- [ ] **TH.SEC06** Secret management and rotation; encryption at rest; PII in logs
- [ ] **TH.SEC07** Threat model: refund flow and supplier portal boundary

## Django and ORM (stages 15, 22, 24)

- [ ] **TH.DJ01** Django ORM vs SQLAlchemy: QuerySet laziness, select_related vs prefetch_related
- [ ] **TH.DJ02** annotate, aggregate, F/Q, Subquery, raw SQL, RunSQL
- [ ] **TH.DJ03** Migrations: Django vs Alembic; expand/contract
- [ ] **TH.DJ04** Signals and why the service layer instead
- [ ] **TH.DJ05** WSGI vs ASGI for Django
- [ ] **TH.DJ06** DRF: serializers, ViewSets, permissions, throttling, pagination

## Networking and Linux (stages 0, 12, 18, 21)

- [ ] **TH.NET01** TCP handshake, retransmission, keep-alive
- [ ] **TH.NET02** DNS
- [ ] **TH.NET03** TLS handshake and certificates
- [ ] **TH.NET04** HTTP/1.1 vs 2 vs 3; WebSocket protocol
- [ ] **TH.NET05** Processes, threads, signals
- [ ] **TH.NET06** Containers: namespaces, cgroups
- [ ] **TH.NET07** Debugging tools: ps, top, ss, lsof, strace, tcpdump, curl -v

## Algorithms (regularly)

- [ ] **TH.AL01** Arrays, hash maps, two pointers, sliding window
- [ ] **TH.AL02** Stacks, queues, heaps
- [ ] **TH.AL03** Binary search
- [ ] **TH.AL04** Trees, BFS, DFS
- [ ] **TH.AL05** Graph basics
- [ ] **TH.AL06** Dynamic programming basics
