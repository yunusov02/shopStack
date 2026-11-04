# Stage 37: Data quality, contracts, governance and observability

Where: `data/quality`, `data/contracts`, Grafana. Prerequisites: stages 35 and 20.

## Data contracts `[CORE]`

- [ ] **S37.T01** ADR 0067: JSON Schema vs Avro for event contracts; schema registry choice (Apicurio vs Confluent vs repo-only)
  Must know: schema formats, compatibility modes

- [ ] **S37.T02** Contracts in `data/contracts/`: one schema per consumed event and CDC table; compatibility check in the core's CI (a breaking change fails the producer's build)
  Must know: backward/forward compatibility

- [ ] **S37.T03** Schema registry in Compose with compatibility enforcement; Debezium schema changes flowing to Silver without breakage (test: add a column to `products`)
  Must know: registry integration, schema evolution

- [ ] **S37.T04** Schema evolution policy document (what needs notice, what needs a version), covering events, CDC, Gold tables consumed by ML and Analytics
  Must know: contract governance

## Data quality `[CORE]`

- [ ] **S37.T05** ADR 0068: dbt tests vs Great Expectations; where each runs
  Must know: quality tooling

- [ ] **S37.T06** Quality dimension tests (completeness, accuracy, consistency, timeliness, uniqueness, validity) as dbt and/or GE suites on Silver and Gold
  Must know: data quality dimensions

- [ ] **S37.T07** Deduplication as an explicit step with tests: events by `event_id`, CDC by `(table, pk, lsn)`; offline-sync duplicates as the fixture
  Must know: dedup keys, LSN

- [ ] **S37.T08** Quality gates in DAGs: critical failure stops downstream and alerts; warnings load with a flag; quarantine tables with reasons
  Must know: gates, quarantine pattern

- [ ] **S37.T09** Volume anomaly checks per tenant per day vs rolling baseline; alert with runbook
  Must know: volume baselines

## Governance and privacy `[CORE]`

- [ ] **S37.T10** ADR 0069: PII policy for the lake (HMAC pseudonymisation with per-tenant keys in the core, Bronze retention, mapping only in the core)
  Must know: pseudonymisation, HMAC, retention

- [ ] **S37.T11** Pseudonymisation step Bronze → Silver; test that no raw phone/name reaches Silver or Gold; payroll rule (no personal amounts) enforced by a test
  Must know: PII detection tests

- [ ] **S37.T12** Deletion propagation job: right-to-be-forgotten request → delete-by-key across all layers (Iceberg deletes) with a completion record
  Must know: deletes in Iceberg, proof of deletion

- [ ] **S37.T13** Warehouse access control: roles per persona, RLS by `tenant_id`, column masking for PII, query logging with principal
  Must know: Postgres roles, RLS, masking

- [ ] **S37.T14** Lineage and catalog: OpenLineage from Airflow and dbt into a lineage store; owner and description on every Gold table; "what breaks if X changes" query
  Must know: OpenLineage, dbt docs

- [ ] **S37.T15** Retention and cost: MinIO lifecycle rules per layer; storage cost per tenant per month as a metric
  Must know: lifecycle policies, cost metrics

## Observability `[CORE]`

- [ ] **S37.T16** Freshness SLOs: `now() − max(loaded_at)` per Gold table to Prometheus; symptom-based alerts with runbooks
  Must know: freshness metrics, SLOs

- [ ] **S37.T17** Pipeline metrics and a Grafana dashboard: DAG durations, rows in/out, rejected rows, Bronze consumer lag, Debezium slot lag
  Must know: pipeline observability

- [ ] **S37.T18** Incident drills: planted schema break and planted duplicate burst, both caught by gates; two postmortems
  Must know: postmortem template

## Extensions

- [ ] **S37.T19** `[EXT]` Nightly reconciliation dashboard (lake vs core counts, Gold vs ledger); data SLA documents per consumer; `CODEOWNERS` per schema
  Must know: data SLAs, ownership

- [ ] **S37.T20** `[EXT]` DataHub or OpenMetadata as the catalog (ADR); `[OPT]` data-access audit to the Audit service
  Must know: catalog services
