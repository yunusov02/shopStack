# Stage 9: Async jobs, caching and bulk operations

Where: `worker/`, `tasks.py` per module. Prerequisites: stage 5. Done when no tasks are lost on worker restart and a 100,000-row import passes without memory problems.

## Celery and RabbitMQ `[CORE]`

- [ ] **S9.T01** RabbitMQ in Compose (management UI), Celery app in `worker/celery_app.py`, settings for broker/result backend
  Must know: Celery basics, AMQP, Compose services

- [ ] **S9.T02** ADR 0019: Celery vs arq/taskiq
  Must know: sync vs async workers

- [ ] **S9.T03** Sync SQLAlchemy engine/session for workers (psycopg) and a sync UoW
  Must know: sync SQLAlchemy, psycopg, two engines

- [ ] **S9.T04** Tenant context in tasks: every task takes `tenant_id`, sets the context var and `SET LOCAL` in its transaction
  Must know: contextvars in workers, RLS in workers

- [ ] **S9.T05** After-commit dispatch: UoW collects queued tasks and sends them only after a successful commit
  Must know: outbox-lite, commit hooks

- [ ] **S9.T06** Retries with exponential backoff and jitter, `acks_late=True`, `task_reject_on_worker_lost`, idempotent task design (`task_id`/dedup key)
  Must know: at-least-once, idempotency, Celery retry options

- [ ] **S9.T07** Queues: `default`, `high`, `low`; routing per task; prefetch count as backpressure; Dead-letter queue for poison messages
  Must know: queue routing, prefetch, DLQ

- [ ] **S9.T08** Celery beat with a schedule table and Flower in Compose
  Must know: periodic tasks, Flower

- [ ] **S9.T09** Move OTP and invite sending to Celery tasks through the SMS port
  Must know: task refactor

- [ ] **S9.T10** Worker restart test: enqueue, kill worker mid-task, restart, task completes exactly once (idempotency)
  Must know: `acks_late` behaviour, integration test with Celery worker

- [ ] **S9.T11** Move earlier CLI jobs (expired reservations, expired batches, points expiry, birthday promos) to beat tasks
  Must know: scheduled tasks

## Cache `[CORE]`

- [ ] **S9.T12** ADR 0020: cache-aside vs write-through vs write-back for catalog, prices, domains
  Must know: cache patterns

- [ ] **S9.T13** `Cache` helper: tenant-prefixed keys, TTL, JSON serialization with Decimal support, hit/miss counters
  Must know: redis-py, key design, serialization

- [ ] **S9.T14** Cache catalog lookups and resolved prices; invalidate on product/price change (service layer)
  Must know: invalidation on write

- [ ] **S9.T15** Stampede protection: per-key lock with TTL or early refresh; thundering herd test with parallel misses
  Must know: cache stampede, locks with TTL

- [ ] **S9.T16** Eviction policy configured (`maxmemory-policy allkeys-lru`), warm-up task after deploy for hot tenants; hot key note in README
  Must know: Redis eviction, LRU vs LFU

- [ ] **S9.T17** Tests: hit/miss, invalidation, stampede lock
  Must know: Redis in tests (Testcontainers)

## Distributed lock `[CORE]`

- [ ] **S9.T18** Redis lock: `SET NX PX` with a random token, release via Lua compare-and-delete, extend
  Must know: Redis locks, Lua scripts, token ownership

- [ ] **S9.T19** Apply to singleton beat jobs (reconciliation, expiry)
  Must know: singleton jobs

- [ ] **S9.T20** ADR 0021: why stock uses DB locks, not Redis locks; Redlock debate
  Must know: lock safety, fencing tokens

## Import/export `[CORE]`

- [ ] **S9.T21** `ImportJob` model + migration: file, status, progress, error report path
  Must know: job tracking tables

- [ ] **S9.T22** Upload endpoint → stored file → Celery task; streamed CSV/XLSX parsing in chunks; upsert (`INSERT ... ON CONFLICT`) by SKU/barcode; error report
  Must know: streaming file parsing, upsert, memory limits

- [ ] **S9.T23** Progress endpoint (polling); `[EXT]` SSE endpoint for progress; ADR 0022 polling vs SSE vs WebSocket
  Must know: SSE, `StreamingResponse`

- [ ] **S9.T24** Product export (CSV) streamed from a server-side cursor
  Must know: `yield_per`, streaming responses

- [ ] **S9.T25** 100k-row import test under a memory limit; no duplicates on re-upload
  Must know: memory profiling (`tracemalloc`)

## Bulk operations `[CORE]`

- [ ] **S9.T26** Bulk price update task: filter → new prices → history + audit entries in batches
  Must know: batch updates, `executemany`

- [ ] **S9.T27** `bulk_create` with RLS: set `app.tenant_id`, insert in batches, measure vs row-by-row
  Must know: bulk inserts, RLS and bulk

## WebSocket `[EXT]`

- [ ] **S9.T28** FastAPI WebSocket endpoint with auth; Redis pub/sub fan-out across instances
  Must know: WebSocket, pub/sub

- [ ] **S9.T29** Remote manager approval over WebSocket (S5.T37) and a live sales dashboard channel
  Must know: push notifications design
