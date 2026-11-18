# Phase I specs: data and ML

Code lives in `data/` and `ml/`; the platform never writes to the core database.

### 48 · Any past question can be answered

**Files:** `data/ingest/kafka_to_bronze.py`, `data/cdc/debezium-postgres.json`, `data/transforms/silver/*.py`, `data/dags/*.py`, `notebooks/explore.ipynb`, `docs/runbooks/data/*`

**Tables:** `bronze.events` (raw envelopes, partitioned by `tenant_id` and date), `bronze.cdc_<table>`; `silver.sales`, `silver.sale_lines`, `silver.products` (deduplicated, typed)

**Steps**

1. MinIO buckets; Iceberg with a SQL catalog on Postgres (`pyiceberg`).
2. Kafka consumer writes Parquet micro-batches to Bronze.
3. Silver job deduplicates by `event_id`, casts types, handles late data.
4. Debezium on products, customers and locations; alert on replication slot lag.
5. Every job overwrites whole partitions, so reruns are safe; backfill reads a replica.
6. Airflow DAGs with retries; DuckDB notebook; pandas vs Polars at 10M rows.

**Done when:** rerunning a day gives identical counts and checksums; `silver.sales` matches the core's completed sales for that day; the slot-lag alert fires in a drill.

### 49 · Revenue in the warehouse equals the ledger

**Files:** `data/dbt/{models/staging,models/intermediate,models/marts,snapshots,tests}`, `data/dags/dbt.py`

**Models:** `fct_sales`, `fct_sale_lines`, `dim_product` (SCD2 snapshot), `dim_customer`, `dim_location`, `dim_date`; Gold aggregates

**Steps**

1. Staging from Silver; SCD2 snapshot for products; star-schema marts.
2. dbt tests (`not_null`, `unique`, `relationships`) plus a custom test reconciling revenue to a GL export.
3. Incremental models; dbt docs; `dbt build` on sample data in CI; nightly run from Airflow.
4. The Analytics dashboard reads Gold.

**Done when:** Gold revenue equals the GL to the tiyin; an as-of query shows a product's historical price correctly.

### 50 · Big aggregates run in minutes

**Files:** `data/spark/batch_aggregates.py`, `data/spark/streaming_sales_per_minute.py`, `data/spark/README.md`

**Steps**

1. Local Spark cluster in Docker; batch aggregate over 10M+ lines.
2. Find the skew from the largest tenant; fix with salting; enable AQE; broadcast small dimensions.
3. Structured Streaming from the `sales` topic: 1-minute event-time windows, 10-minute watermark, Iceberg sink, checkpoints.
4. Kill and restart the stream.

**Done when:** after the restart, counts equal the source with no gaps or duplicates; the README has before/after times.

### 51 · Bad data never reaches Gold

**Files:** schema registry config, `data/quality/*`, `data/pii/policy.md`, OpenLineage config

**Steps**

1. Schema registry with `BACKWARD` compatibility; the core's CI checks new event schemas against it.
2. A data contract per Silver table: owner, schema, SLA.
3. Quality checks (counts, nulls, ranges, freshness) gate Gold; failing rows go to quarantine.
4. Phones hashed with a tenant salt in Silver; deletion requests reach every layer through Iceberg deletes.
5. OpenLineage from Airflow and dbt; freshness SLO alerts.

**Done when:** a breaking schema change fails CI; an injected bad batch lands in quarantine with Gold unchanged; a deletion request removes a customer everywhere.

### 52 · A model beats the forecast baseline

**Files:** `ml/features/*`, `ml/training/{forecast,churn,segmentation}.py`, `ml/backtest.py`; MLflow in Compose

**Steps**

1. Point-in-time correct features with as-of joins.
2. Forecast (a global LightGBM model or ETS per series) vs the slice 43 baseline on a rolling-origin backtest, measured with WAPE.
3. Churn: label = no purchase in 60 days; calibrated classifier; Brier score.
4. Segmentation: RFM + k-means.
5. Leakage checklist per model; every run tagged with the data snapshot ID and git SHA.

**Done when:** the forecast beats the baseline's WAPE; rerunning a run ID reproduces its metrics.

### 53 · Models ship without copying files

**Files:** `services/ml-serving/`, `ml/pipelines/{train,evaluate,promote}.py`, `data/dags/ml.py`, Helm chart

**Steps**

1. MLflow registry aliases; serving loads by alias with a 200 ms timeout and a baseline fallback.
2. Nightly batch inference → `forecast.published.v1` (consumed by planning); `customer_segment.changed.v1`.
3. Shadow mode, then a 10% canary; `model.deployed.v1`.
4. Drift monitoring (PSI on features and predictions); weekly retraining DAG; rollback alert when live WAPE gets worse.

**Tests**

- `test_serving_falls_back_on_timeout`
- `test_shadow_model_does_not_affect_response`
- A drift alert fires on an injected shift

### 54 · Recommendations prove themselves in an A/B test

**Files:** `ml/recsys/{item_item,als,evaluate}.py`, `modules/experiments/*`, `modules/anomaly/*`, serving routes

**Steps**

1. Baselines: most popular; item-item co-occurrence; ALS with `implicit`; NDCG@10 on a time split.
2. pgvector embeddings for hybrid product search with FTS.
3. Experiments: assignment by `hash(user, experiment)`, `experiment.exposed.v1`, metrics in the warehouse, power analysis before launch.
4. Isolation forest over cashier voids, refunds and discounts; `anomaly.detected.v1`; manager reviews stored as labels.

**Done when:** the recommender beats "most popular" offline and an A/B test reaches a decision on a pre-registered metric.

### 55 · Managers ask questions in plain language

**Files:** `services/assistant/{api,llm,rag,sql,tools,evals}`

**Steps**

1. Provider adapter (ADR), token budgets per tenant, PII redaction before prompts.
2. RAG over help pages and policies with pgvector; every retrieval filtered by `tenant_id`.
3. Text-to-SQL over Gold only: read-only role, allowlisted schemas, parsed and validated with `sqlglot`, row limit, timeout.
4. Tools: drafting a PO goes through workflow approvals, never auto-approved.
5. Golden set of 100 questions; evals in CI; cost and latency dashboard; prompt-injection cases from retrieved documents.

**Tests**

- `test_retrieval_never_crosses_tenants`
- `test_generated_sql_rejected_unless_select_on_gold`
- `test_agent_po_requires_approval`
- An eval regression blocks the deploy
