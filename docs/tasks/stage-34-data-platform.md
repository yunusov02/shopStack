# Stage 34: Data platform foundation (lakehouse, ingestion, orchestration)

Where: `data/` (`data/ingestion`, `data/dags`, `data/lake`), `notebooks/`. Prerequisites: stages 16 and 23.

## Storage and layout `[CORE]`

- [ ] **S34.T01** ADR 0060: lakehouse on MinIO + Parquet + Iceberg vs "just ClickHouse" vs "bigger Postgres"; OLTP vs OLAP written with this project's numbers
  Must know: OLTP vs OLAP, lake vs warehouse vs lakehouse

- [ ] **S34.T02** MinIO bucket `lake` with separate credentials and policies; prefixes `bronze/`, `silver/`, `gold/`; Compose and Makefile targets
  Must know: S3 API, bucket policies

- [ ] **S34.T03** Format lab: write 10M seeded sale lines as JSON, Avro and Parquet; table of size, write time, time to read two columns; `DECIMAL` for money; results in README
  Must know: columnar storage, row groups, predicate pushdown

- [ ] **S34.T04** Iceberg catalog backed by Postgres (PyIceberg); first table `bronze.sale_events` partitioned by `tenant_id`, `event_date`; schema evolution test (add a column) and time-travel query
  Must know: Iceberg catalog, snapshots, partition spec

- [ ] **S34.T05** Compaction job for small files; target file size and a measurement of query time before/after
  Must know: small-file problem, compaction

- [ ] **S34.T06** Layer contract in `data/README.md`: Bronze schema-on-read (raw JSON kept), Silver schema-on-write (typed, deduplicated, pseudonymised in S37), Gold business-ready
  Must know: schema-on-read vs schema-on-write, medallion

## Ingestion `[CORE]`

- [ ] **S34.T07** Bronze event consumer: Kafka consumer group writing all domain events to `bronze.<event_type>` in micro-batches; offset committed after the Iceberg commit; graceful shutdown
  Must know: consumer groups, at-least-once, micro-batching

- [ ] **S34.T08** Silver event tables: typed columns from the envelope and payload, deduplicated by `event_id` (dedup test with a planted duplicate burst)
  Must know: deduplication, idempotent writes

- [ ] **S34.T09** ADR 0061: outbox events vs CDC; which tables come through CDC (dimensions) and why facts stay as events
  Must know: CDC, logical replication, outbox

- [ ] **S34.T10** Debezium in Compose: Postgres publication limited to dimension tables, `cdc.core.<table>` topics, initial snapshot; Bronze CDC consumer
  Must know: Debezium connector config, publications, snapshots

- [ ] **S34.T11** Replication slot monitoring: WAL growth when the consumer is stopped, a Prometheus metric for slot lag, a runbook
  Must know: replication slots and WAL retention

- [ ] **S34.T12** Incremental vs full load: watermark-based incremental Silver load for events, periodic full reload for small dimensions; ADR note on the choice per table
  Must know: watermark columns, late data

- [ ] **S34.T13** Idempotent partition writes: write to a staging location, atomic Iceberg replace of the partition; test that re-running produces identical files
  Must know: atomic commits, idempotency

- [ ] **S34.T14** Backfill CLI: rebuild Bronze/Silver for a date range from Kafka or from the core's partitioned sales table via a read replica (never the primary)
  Must know: backfill strategies, read replicas

## Orchestration `[CORE]`

- [ ] **S34.T15** ADR 0062: Airflow vs Dagster vs Prefect
  Must know: scheduler models, assets vs tasks

- [ ] **S34.T16** Airflow in Compose (scheduler, webserver, Postgres metadata DB); `data/dags/` mounted; connections and variables from env
  Must know: Airflow architecture

- [ ] **S34.T17** DAG `silver_daily`: sensor on Bronze partition → Silver load → compaction; `data_interval`, retries with backoff, SLA; no logic in DAG files
  Must know: DAG design, sensors, data intervals

- [ ] **S34.T18** DAG `cdc_dimensions`: CDC Bronze → Silver current-state tables; full-reload path for small dimensions
  Must know: current-state from change log

- [ ] **S34.T19** Backfill through Airflow (`catchup`, CLI backfill for a month); outputs per `run_id` swapped atomically; runbook `docs/runbooks/data-platform.md`
  Must know: catchup, backfill, runbooks

## Local analysis `[CORE]`

- [ ] **S34.T20** DuckDB over MinIO: notebook answering three stage 16 questions straight from Silver; note on when a single node stops being enough
  Must know: DuckDB, httpfs/S3, Iceberg scan

- [ ] **S34.T21** pandas vs Polars lab on one transformation at 10M rows; lazy evaluation in Polars; results in README
  Must know: pandas, Polars, lazy frames

## Tests and done `[CORE]`

- [ ] **S34.T22** Integration tests with Testcontainers (Kafka, MinIO, Postgres): event → Bronze → Silver within five minutes; byte-identical rerun; backfill never touches the primary
  Must know: Testcontainers for Kafka and MinIO

## Extensions

- [ ] **S34.T23** `[EXT]` Partition evolution and hidden partitioning; bucketing on `variant_id` measured
  Must know: Iceberg partition evolution

- [ ] **S34.T24** `[EXT]` External files into Bronze with a manifest (stage 9 imports, stage 25 payouts); Airflow on Kubernetes with the Kubernetes executor
  Must know: file manifests, Kubernetes executor

- [ ] **S34.T25** `[OPT]` Kafka Connect Iceberg sink instead of hand-written consumers; lakeFS or Iceberg branches; Dagster spike with a written comparison
  Must know: Kafka Connect, lakeFS
