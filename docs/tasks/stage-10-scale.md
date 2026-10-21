# Stage 10: Scale, performance and search

Prerequisites: stage 9. Done when before/after results for every report are in the README.

## Data and plans `[CORE]`

- [ ] **S10.T01** Seed script: 10M+ sale lines, one very large tenant, realistic distributions; runs in batches
  Must know: data generation, `COPY`, batching

- [ ] **S10.T02** `EXPLAIN (ANALYZE, BUFFERS)` on every report: record seq/index/bitmap scans and join strategies in README
  Must know: reading plans, join strategies

- [ ] **S10.T03** Indexes: composite, partial (`deleted_at IS NULL`, status), covering (`INCLUDE`), BRIN on `created_at`, GIN on JSONB; measure each
  Must know: index types, index-only scans

- [ ] **S10.T04** `pg_stat_statements` enabled; top queries report script
  Must know: `pg_stat_statements`

- [ ] **S10.T05** SQL lab: one report written with INNER/LEFT joins, with `EXISTS` (semi/anti join), with window functions; compare plans
  Must know: join types, window functions, `FILTER`

## ORM performance `[CORE]`

- [ ] **S10.T06** Query counter test helper (SQLAlchemy events); assert query counts on list endpoints
  Must know: `before_cursor_execute` event, N+1

- [ ] **S10.T07** Set `lazy="raise"` on all relationships; fix every N+1 with `selectinload`/`joinedload`
  Must know: loader strategies

- [ ] **S10.T08** Whitelisted filtering and sorting helper; offset vs cursor pagination measured at page 10,000
  Must know: keyset pagination, `OFFSET` cost

- [ ] **S10.T09** Soft delete + partial indexes applied project-wide
  Must know: partial indexes

## Partitioning and summaries `[CORE]`

- [ ] **S10.T10** Partition `sales` and `sale_lines` by month (`RANGE` on `completed_at`); migration with data move; beat task creating future partitions
  Must know: declarative partitioning, partition pruning, PK with partition key

- [ ] **S10.T11** Summary tables (daily sales per location/variant) refreshed by task, or materialized views with `REFRESH CONCURRENTLY`; ADR 0023 on denormalization and consistency
  Must know: materialized views, denormalization

- [ ] **S10.T12** Hotspot experiment: the giant tenant and one hot Redis key; what degrades, mitigation notes (ADR)
  Must know: hotspots, hot keys

## Full-text search `[CORE]`

- [ ] **S10.T13** `tsvector` column with trigger/generated column, GIN index; `pg_trgm` fallback
  Must know: FTS, `to_tsvector`, GIN

- [ ] **S10.T14** Latin↔Cyrillic transliteration for Uzbek and Russian; index both forms
  Must know: transliteration tables, normalization

- [ ] **S10.T15** Search endpoint ranking (`ts_rank`), tests with mixed scripts
  Must know: ranking, test data in two scripts

## Pooling and profiling `[CORE]`

- [ ] **S10.T16** PgBouncer in Compose (transaction pooling); `SET LOCAL` compatibility; asyncpg prepared statements fix (`statement_cache_size=0` or named statements)
  Must know: PgBouncer modes, prepared statements problem

- [ ] **S10.T17** SQLAlchemy pool tuning (`pool_size`, `max_overflow`, `pool_timeout`); exhaust the pool under load and record behaviour
  Must know: connection pooling

- [ ] **S10.T18** Profiling: `py-spy` flame graph and `memray` on a worker; plant and find one bottleneck and one leak
  Must know: profiling tools, memory leaks

- [ ] **S10.T19** `[EXT]` Streaming read replica in Compose, read-only session for reports, replication lag measured
  Must know: streaming replication, lag

- [ ] **S10.T20** `[OPT]` OpenSearch index synced from events; ADR 0024 when Postgres FTS is not enough
  Must know: OpenSearch basics
