# Phase D specs: load, performance and background work

Every slice here ends with a before/after table in the README.

### 15 · 50 cashiers sell at once

**Files:** `load/locustfile.py`, `load/README.md`, `core/db_retry.py`, `modules/sales/locking.py`, `tests/labs/test_isolation_anomalies.py`

**Models:** `stock_levels`: add `version int` for the optimistic variant.

**Steps**

1. Locust: 50 users, each with its own open shift; every sale takes 3 lines from a hot set of 20 variants, pays and completes with an `Idempotency-Key`.
2. Record p50, p95, p99 and error rate.
3. Turn off lock ordering with a flag, watch `40P01` deadlocks, turn it back on.
4. `@retry_on_conflict`: retries `40001` and `40P01` with jitter, at most 3 times.
5. Optimistic variant: `UPDATE ... WHERE version = :v`, retry when 0 rows change. Measure both under hot contention; ADR.
6. Isolation lab: reproduce lost update, non-repeatable read, phantom and write skew; show which Postgres level prevents each.
7. Run the sale at `SERIALIZABLE` with retries and compare throughput.
8. `begin_nested()` savepoint around the payment adapter call.

**Tests**

- `test_lost_update_reproduced_at_read_committed`
- `test_repeatable_read_prevents_non_repeatable_read`
- `test_write_skew_prevented_by_serializable`
- `test_retry_on_deadlock_succeeds`
- `test_payment_failure_rolls_back_to_savepoint_sale_stays_draft`

### 16 · Reports stay fast on 10M lines

**Files:** `scripts/seed_large.py`, `modules/reports/*`, `tests/support/query_counter.py`, `migrations/versions/0016_partitions_summaries.py`

**Models**

- `sales` and `sale_lines` range-partitioned by month on `completed_at`
- `daily_sales_summary`: `tenant_id`, `location_id`, `day`, `variant_id`, `quantity`, `revenue`, `cost`

**Endpoints**

- `GET /api/v1/reports/sales-by-day?from=&to=&location_id=`
- `GET /api/v1/reports/sales-by-product?from=&to=&limit=`
- `GET /api/v1/sales?cursor=&limit=&sort=` (keyset pagination)

**Steps**

1. Seed 10M lines with `COPY`; one tenant holds 60% of them.
2. Write the reports naively; save `EXPLAIN (ANALYZE, BUFFERS)` and the top 10 of `pg_stat_statements`.
3. Indexes: `(tenant_id, completed_at)`, partial on completed sales, covering with `INCLUDE`, BRIN on movement time, GIN on variant attributes.
4. SQL lab: one report written with `GROUP BY`, with window functions and with `FILTER`.
5. Query counter fixture: a fixed number of queries per endpoint; relationships default to `lazy="raise"`.
6. Keyset pagination on `(completed_at, id)`; compare with `OFFSET` at page 10,000.
7. Partition migration: create the partitioned table, copy, swap (ADR).
8. Summary table updated in the completion transaction or nightly (ADR).
9. `py-spy` flame graph of the slowest endpoint; `memray` on an import with a planted leak.

**Tests**

- `test_sales_list_query_count_is_constant`
- `test_cursor_pagination_stable_while_inserting`
- `test_summary_matches_raw_lines`

### 17 · Hot reads stop hitting Postgres

**Files:** `core/cache.py`, `modules/catalog/cache.py`, `scripts/warm_cache.py`

**Steps**

1. From slice 16 profiling, list the hot reads: domain → tenant, variant price, catalog snapshot.
2. `get_or_set(key, loader, ttl)` with keys like `t:{tenant}:price:{variant}:{location}` and jittered TTLs.
3. Invalidation in the Unit of Work's after-commit hook; a version key to invalidate a whole price list.
4. Stampede protection: single-flight with `SET NX PX`.
5. Redis `maxmemory` with `allkeys-lru`; warm-up script after deploy.
6. Hit and miss counters; Locust before and after.

**Tests**

- `test_price_change_invalidates_cache_after_commit`
- `test_rollback_does_not_invalidate`
- `test_100_concurrent_misses_load_once`
- `test_cache_keys_include_tenant`

### 18 · Slow work leaves the request

**Files:** `worker/celery_app.py`, `modules/catalog/imports.py`, `modules/inventory/jobs.py`, `core/uow.py` (after-commit task queue); Compose: `rabbitmq`, `worker`, `beat`

**Models:** `import_jobs`: `id`, `tenant_id`, `file_key`, `status` (`queued`, `running`, `done`, `failed`), `total`, `processed`, `errors jsonb`

**Endpoints**

- `POST /api/v1/imports/products` (multipart) → `202 {job_id}`; `GET /api/v1/imports/{id}`
- `POST /api/v1/prices/bulk-update` → `202`

**Steps**

1. Celery with RabbitMQ; a base task class restores the tenant context from the task kwargs.
2. The Unit of Work collects tasks and sends them only after commit.
3. `acks_late`, `reject_on_worker_lost`, `autoretry_for` transient errors, `retry_backoff` with jitter; queues `imports`, `notifications`, `default`; prefetch 1 for long tasks.
4. Dead-letter exchange for poison messages.
5. Import: read CSV or Excel in chunks of 1,000, validate, `ON CONFLICT (tenant_id, sku)` upsert, update progress.
6. Beat: release expired reservations (every minute), purge idempotency keys (hourly), low-stock check (nightly), each behind a Redis lock.
7. OTP and invite sending become tasks.

**Tests**

- `test_task_not_sent_when_transaction_rolls_back`
- `test_import_100k_rows_upserts_and_reports_errors`
- `test_import_task_idempotent_on_retry`
- `test_expired_reservations_are_released`
- `test_poison_message_goes_to_dlq` (RabbitMQ container)

### 19 · The database survives many connections

**Files:** `deploy/pgbouncer.ini`, `core/db.py`, `modules/catalog/search.py`, `migrations/versions/0019_fts.py`

**Steps**

1. Ramp Locust until the pool times out; record the failure.
2. Tune `pool_size`, `max_overflow`, `pool_timeout`, `pool_pre_ping`; workers × pool must stay under `max_connections`.
3. PgBouncer in transaction mode; disable asyncpg's statement cache; tenant set only with `SET LOCAL`.
4. Full-text search: a `search` column with the name plus its Latin and Cyrillic transliterations, `simple` config + `unaccent`, GIN index; rank with `ts_rank`, fall back to trigram similarity.
5. ADR: one very large tenant as a hotspot.

**Tests**

- `test_cyrillic_query_finds_latin_name`
- `test_typo_tolerant_search_via_trigram`
- `test_tenant_setting_does_not_leak_between_pgbouncer_transactions`
