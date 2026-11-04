# Stage 3: Inventory and warehouses

Where: `modules/inventory`. Prerequisites: stage 2. Done when reconciliation matches after any sequence of operations and the parallel reservation test is green.

## Stock basics `[CORE]`

- [ ] **S3.T01** `StockMovement` model + migration: `tenant_id`, `location_id`, `variant_id`, `type` (`receive | sale | return | transfer_out | transfer_in | adjustment | count | assembly`), `quantity Numeric(12,3)` signed, `reference_type`, `reference_id`, `batch_id`, `created_at`; append-only grants + trigger
  Must know: ledger design, append-only tables, polymorphic reference columns

- [ ] **S3.T02** `StockLevel` model + migration: unique `(location_id, variant_id)`, `on_hand`, `reserved`, generated `available`; `CHECK (on_hand >= 0 AND reserved >= 0 AND reserved <= on_hand)`
  Must know: generated columns, CHECK constraints, composite unique

- [ ] **S3.T03** `StockRepository`: `get_level_for_update(location, variant)` (`with_for_update`), `add_movement`, `upsert_level`
  Must know: `SELECT ... FOR UPDATE`, upsert, row locks

- [ ] **S3.T04** `StockService.apply_movement(...)`: locks the level row, writes the movement and updates the level in one transaction; negative stock → domain error
  Must know: one transaction = movement + balance, lock ordering

- [ ] **S3.T05** Receive endpoint (`inventory.receive`): manual receipt into a location (procurement replaces it in stage 4)
  Must know: FastAPI, permission dependency

- [ ] **S3.T06** `min_stock` and `reorder_level` on `StockLevel` (or a settings table); `stock.low` domain event placeholder (an in-process event bus; Kafka in stage 13)
  Must know: in-process events, threshold checks

- [ ] **S3.T07** Reconciliation job: for every level, `on_hand == SUM(movements)`; report differences; CLI command
  Must know: aggregate queries, `GROUP BY`, CLI

- [ ] **S3.T08** Movement history endpoint with filters (location, variant, type, period) and **cursor pagination** (`(created_at, id)` keyset)
  Must know: keyset pagination, composite index for the cursor

- [ ] **S3.T09** Tests: movement/level consistency, negative stock rejected, reconciliation, cursor pagination
  Must know: integration tests, concurrency fixtures

- [ ] **S3.T10** `[EXT]` Batch and serial movements: `batch_id`/`serial_id` on movements, per-batch levels; FEFO picker (`ORDER BY expires_at`)
  Must know: FEFO, per-batch balances

## Adjustments and stock counts `[CORE]`

- [ ] **S3.T11** `Adjustment` model + migration: lines, `reason` (`damaged | expired | lost | found | correction`), `status`, `approved_by`
  Must know: document + lines pattern

- [ ] **S3.T12** `AdjustmentService`: create → (approve if above threshold, `inventory.adjust` + approval permission) → apply (movements); audit log entry
  Must know: state machine, approval threshold, audit

- [ ] **S3.T13** Adjustment endpoints: create, approve, apply, list
  Must know: FastAPI, state transition endpoints

- [ ] **S3.T14** `StockCount` model + migration: session (`full | partial`), status, `snapshot_at`; `StockCountLine`: expected (snapshot), counted, delta
  Must know: snapshot semantics

- [ ] **S3.T15** `StockCountService`: start (snapshot levels), enter counts, compute variance using snapshot + movements since snapshot, close → generate adjustments → approval
  Must know: snapshot + delta computation, document chaining

- [ ] **S3.T16** Stock count endpoints and variance report
  Must know: reporting queries

- [ ] **S3.T17** Tests: adjustment threshold, count with sales during counting, variance → adjustments
  Must know: integration tests with interleaved operations

- [ ] **S3.T18** `[EXT]` Expired batch detection job (placeholder until Celery in stage 9): list batches past expiry, propose adjustments
  Must know: scheduled jobs, date comparisons in UTC

## Transfers and reservations `[CORE]`

- [ ] **S3.T19** `Transfer` model + migration: from/to location, status (`requested → approved → picking → shipped → received / cancelled`), lines with requested/shipped/received quantities
  Must know: state machine columns, lines with multiple quantities

- [ ] **S3.T20** `transition(transfer, to_state)` function with an allowed-transitions table and a `TransferTransition` log row
  Must know: explicit state machines, transition logging

- [ ] **S3.T21** `TransferService`: approve (`inventory.transfer.approve`), ship (`transfer_out` movements, in-transit level), receive (`transfer_in`, partial quantities, discrepancies recorded)
  Must know: in-transit stock, partial receipt, discrepancy records

- [ ] **S3.T22** Transfer endpoints: request, approve, ship, receive (with per-line received quantities), cancel
  Must know: FastAPI, permission per transition

- [ ] **S3.T23** `Reservation` model + migration: `variant_id`, `location_id`, `quantity`, `reference_type/id`, `expires_at`, `status`
  Must know: TTL columns, reference polymorphism

- [ ] **S3.T24** `ReservationService.reserve(...)`: ADR 0011 pessimistic row lock vs atomic `UPDATE stock_levels SET reserved = reserved + :q WHERE available >= :q`; implement the chosen one; release and expire
  Must know: race conditions, atomic UPDATE, `with_for_update`

- [ ] **S3.T25** Expired reservation release job (CLI now, Celery beat in stage 9)
  Must know: idempotent jobs

- [ ] **S3.T26** Concurrency test: N parallel reservations on the same variant never exceed `available` (asyncio.gather with separate sessions)
  Must know: concurrency tests, separate connections per task

- [ ] **S3.T27** Tests: transfer state machine, partial receipt, in-transit level, reservation expiry
  Must know: integration tests

## Warehouse operations `[EXT]`

- [ ] **S3.T28** `Zone` and `Bin` models + migration (per location); `BinLevel` (bin × variant)
  Must know: hierarchical location data

- [ ] **S3.T29** Put-away service: receive → bin assignment; internal bin-to-bin move recorded as a movement with unchanged `on_hand`
  Must know: internal movements vs stock movements

- [ ] **S3.T30** Picking list generation for transfers and orders; picking route ordered by bin code
  Must know: ordering, batch processing
