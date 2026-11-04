# Stage 36: Batch and stream processing at scale (Spark, Structured Streaming)

Where: `data/jobs`, Spark in Compose (master + 2 workers). Prerequisites: stage 35.

## Spark fundamentals `[CORE]`

- [ ] **S36.T01** ADR 0065: Spark vs Polars/DuckDB on a single large node; when the cluster is worth it
  Must know: single node vs distributed trade-offs

- [ ] **S36.T02** Spark cluster in Compose with Iceberg and S3A configured; first PySpark job reading `silver.sale_events`; `explain()` read and annotated in a note
  Must know: Spark architecture, plans

- [ ] **S36.T03** Shuffle lab: daily aggregate by tenant and product three ways; Spark UI shuffle sizes; `spark.sql.shuffle.partitions`, `repartition` vs `coalesce`; numbers in README
  Must know: shuffle, partitions

- [ ] **S36.T04** Skew lab: one tenant with 80% of rows; salting and AQE skew join; before/after timing
  Must know: data skew, salting, AQE

- [ ] **S36.T05** Join lab: broadcast vs sort-merge with `dim_product`; broadcast threshold; the case where broadcast hurts; bucketed join on `variant_id`
  Must know: join strategies in Spark

- [ ] **S36.T06** Caching and memory lab: `cache`/`persist` levels, executor memory model, a planted spill and a planted OOM, each explained
  Must know: Spark memory management

- [ ] **S36.T07** UDF lab: Python UDF vs pandas UDF vs built-ins on the same transformation, timed
  Must know: Arrow, serialisation cost

- [ ] **S36.T08** Writing back: `MERGE INTO` an Iceberg Gold table, partition overwrite, compaction; idempotent per `run_id`; as an Airflow task
  Must know: Iceberg writes from Spark

## Stream processing `[CORE]`

- [ ] **S36.T09** ADR 0066: Spark Structured Streaming vs Flink vs a Python stream library; micro-batch vs true streaming
  Must know: streaming engines

- [ ] **S36.T10** Streaming job `sales_per_minute`: Kafka source, event time from `occurred_at`, tumbling window, watermark, Gold sink; served by the stage 16 dashboard
  Must know: event time, tumbling windows, watermarks

- [ ] **S36.T11** Late-data lab with offline POS replays (stage 12): what the watermark drops; sliding and session windows for cashier activity
  Must know: late data, window types

- [ ] **S36.T12** Stateful streaming: running totals per shift, checkpoint to MinIO, kill-and-restart test proving no loss and no duplicates; exactly-once via idempotent sink
  Must know: state stores, checkpoints, exactly-once output

- [ ] **S36.T13** Backpressure: `maxOffsetsPerTrigger`, consumer lag metric to Prometheus, effect on the watermark
  Must know: backpressure in streams

- [ ] **S36.T14** Stream-table join with `dim_product` (SCD2 in a stream) and stream-stream join of orders and deliveries with a time bound
  Must know: stream joins

- [ ] **S36.T15** Tests: streaming output equals batch aggregate for every closed window; skewed job under one third of original time
  Must know: testing streaming jobs

## Extensions

- [ ] **S36.T16** `[EXT]` Spark on Kubernetes (operator or `spark-submit`), dynamic allocation, as an Airflow task; cold-cluster cost measured
  Must know: Spark on Kubernetes

- [ ] **S36.T17** `[EXT]` Replay the live Gold table from a chosen offset and compare with batch (Lambda vs Kappa with numbers)
  Must know: Lambda vs Kappa

- [ ] **S36.T18** `[OPT]` Same job in Polars streaming mode and DuckDB; same streaming job in PyFlink; MapReduce/Hadoop/HDFS history note
  Must know: engine comparison
