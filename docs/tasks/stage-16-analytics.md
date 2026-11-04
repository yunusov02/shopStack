# Stage 16: Analytics service (FastAPI)

Where: `services/analytics`. Prerequisites: stage 15.

- [ ] **S16.T01** Service skeleton: FastAPI, async SQLAlchemy, Alembic, own DB, Dockerfile, CI
  Must know: service template

- [ ] **S16.T02** Kafka consumer: commit offset after write, replay from beginning CLI
  Must know: consumer groups, offsets

- [ ] **S16.T03** `ProcessedEvent` table and idempotent projection base; out-of-order and late events; refunds correct earlier figures
  Must know: idempotent projections

- [ ] **S16.T04** Read models: daily sales per location/cashier/category/product/hour/weekday; customer totals; stock snapshots
  Must know: read model design

- [ ] **S16.T05** Tenant isolation in every query; "today" in tenant time zone
  Must know: time zones in reporting

- [ ] **S16.T06** JWT via JWKS (RS256) auth; Pact contract tests against the monolith's events
  Must know: JWKS, Pact

- [ ] **S16.T07** Dashboard endpoint: today's revenue, profit, receipts, average receipt, items, return share
  Must know: aggregation endpoints

- [ ] **S16.T08** Deep analysis endpoints: by dimension, top customers, slow/dead stock, turnover, ABC
  Must know: ABC analysis, inventory turnover

- [ ] **S16.T09** Strangler fig: run alongside monolith reports, compare, switch back-office to the service
  Must know: parallel run and comparison

- [ ] **S16.T10** Rebuild-from-scratch test: wipe DB, replay, results equal monolith
  Must know: event replay

- [ ] **S16.T11** `[EXT]` Low-stock forecast and reorder suggestions
  Must know: moving average, exponential smoothing

- [ ] **S16.T12** `[OPT]` ClickHouse: MergeTree tables, materialized views; ADR 0034
  Must know: ClickHouse basics
