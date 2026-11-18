# Phase F specs: offline POS and events

### 25 · A store keeps selling without internet

**Files:** `frontend/apps/pos-terminal/` (Vite + React + TS): `src/db/schema.ts`, `src/sync/{snapshot,changes,outbox}.ts`, `src/pricing/engine.ts`, `src/sw.ts`; backend `modules/devices/*`, `modules/sync/{router,service,conflicts}.py`, `migrations/versions/0025_devices_sync.py`

**Models**

- `devices`: `id`, `tenant_id`, `location_id`, `name`, `credential_hash`, `registered_by`, `last_seen_at`, `revoked_at`
- `sync_batches`: `id`, `device_id`, `batch_id UNIQUE`, `received_at`, `status`
- `sales`: add `client_id uuid UNIQUE`, `device_id`, `device_created_at`, `offline bool`
- `sync_conflicts`: `sale_id`, `kind` (`negative_stock`, `price_changed`, `promo_limit`, `credit_limit`, `deleted_product`), `details jsonb`, `resolved_by`, `resolved_at`
- Catalog tables: `deleted_at` tombstones and an `updated_at` index

**Endpoints**

- `POST /api/v1/devices/register` `{one_time_code}` → device credential
- `GET /api/v1/sync/snapshot` (gzipped catalog, prices, promotions as data, customers, with a version)
- `GET /api/v1/sync/changes?since=`
- `POST /api/v1/sync/sales` `{batch_id, sales: [...]}` → status per sale
- Back-office `GET /conflicts`

**Steps**

1. ADR: PWA vs desktop. Service worker caches the app shell.
2. IndexedDB stores for catalog, prices, promotions, customers, outbox.
3. Device registration with a one-time code from the back-office.
4. Snapshot first, then changes by `updated_at` cursor with tombstones.
5. Offline sale with a client UUID; receipt number with a device prefix.
6. Pricing engine in TS runs the slice 21 JSON vectors; offline policy limits duration, amount, refunds and credit.
7. Outbox with exponential retry; server deduplicates by `client_id`, accepts batches out of order, completes sales and records conflicts instead of rejecting them.
8. Store device time and server time separately.

**Tests**

- Shared pricing vectors pass in pytest and vitest
- `test_same_batch_twice_creates_no_duplicates`
- `test_out_of_order_batches_accepted`
- `test_offline_sale_of_deleted_product_creates_conflict`
- `test_negative_stock_reported_as_conflict`
- Playwright: go offline, sell 3 items, reconnect, the sales appear in the back-office

### 26 · Modules stop reaching into each other

**Files:** `.importlinter`, `modules/*/api.py`, `docs/adr/NNNN-module-boundaries.md`

**Steps**

1. Draw the allowed dependency graph; each module exposes only `api.py`.
2. Contracts: layers and forbidden imports of other modules' `models`, `repository`, `service`.
3. Run `lint-imports` in CI.
4. Replace cross-module ORM joins with calls to `api.py` or SQL views owned by the reporting module (documented exception).
5. Drop FKs into `tenancy` and `accounts`, which Platform will own; keep the IDs.

**Tests**

- `lint-imports` passes in CI
- The full test suite still passes

### 27 · Side effects after a sale are never lost

**Files:** `core/outbox.py`, `relay/main.py`, `core/events/{envelope,registry}.py`, `modules/*/events.py`, `docs/events/*.md`; Compose: Kafka in KRaft mode; `migrations/versions/0027_outbox.py`

**Models**

- `outbox`: `id uuid`, `tenant_id`, `aggregate_type`, `aggregate_id`, `event_type`, `event_version`, `payload jsonb`, `occurred_at`, `correlation_id`, `published_at NULL`; partial index on unpublished rows
- `inbox`: `consumer`, `event_id`, `processed_at`; PK `(consumer, event_id)`

**Steps**

1. RFC: Kafka vs RabbitMQ for domain events.
2. Event dataclasses with a version; `uow.add_event()` inserts into `outbox` in the same transaction.
3. Relay: `SELECT ... WHERE published_at IS NULL ORDER BY occurred_at FOR UPDATE SKIP LOCKED LIMIT 100`; topic per aggregate (`sales`, `stock`, `customers`), key `tenant_id`; idempotent producer with `acks=all`; mark published.
4. Backlog size metric.
5. One doc page per event type with its schema; versioning rules.
6. Consumer helper that deduplicates through `inbox`.
7. CI builds the app and relay images.

**Tests**

- `test_event_written_only_when_transaction_commits`
- `test_relay_preserves_order_per_tenant` (Kafka container)
- `test_two_relays_do_not_publish_twice`
- `test_consumer_ignores_duplicate_event`
- `test_envelope_matches_documented_schema`
