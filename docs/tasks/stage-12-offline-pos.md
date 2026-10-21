# Stage 12: Offline POS

Where: `pos-terminal/` (React + TS PWA), `modules/sync`. Prerequisites: stages 7 and 9. Done when a terminal works offline for 1 hour and syncs without duplicates.

## Terminal

- [ ] **S12.T01** ADR 0025: PWA + IndexedDB vs desktop app
  Must know: PWA, service workers, IndexedDB

- [ ] **S12.T02** `Device` model + migration: location, device credentials (hashed secret), status; registration endpoint and device token auth
  Must know: device credentials, token auth

- [ ] **S12.T03** Snapshot endpoint: catalog, prices, promotions, customers for a location (paged, compressed)
  Must know: large responses, gzip, paging

- [ ] **S12.T04** Incremental sync endpoint: `updated_since` cursor, tombstones for deletions (`deleted_at` on entities)
  Must know: change tracking, tombstones

- [ ] **S12.T05** React + TS PWA skeleton: login, download snapshot into IndexedDB, product search offline
  Must know: React, TypeScript, Dexie/IndexedDB

- [ ] **S12.T06** Offline cart and sale with client-generated UUID; device-prefixed receipt numbers
  Must know: UUID v4/v7, local numbering

- [ ] **S12.T07** ADR 0026: pricing offline (rules as data on the client; server recalculates or accepts within policy); port the engine rules format
  Must know: sharing logic as data

- [ ] **S12.T08** Offline policy settings: max duration, max amount, refunds/credit allowed offline
  Must know: policy enforcement on client and server

## Sync

- [ ] **S12.T09** Client outbox in IndexedDB; batch upload with retries and backoff
  Must know: outbox on the client, retry logic

- [ ] **S12.T10** `SyncService.accept_batch()`: idempotent by sale UUID, out-of-order batches, per-sale result (accepted / conflict)
  Must know: idempotency, unique constraints

- [ ] **S12.T11** Conflict handlers: negative stock (accept + flag), price changed (keep client price + audit), promo limit exceeded, credit limit exceeded, product deleted
  Must know: conflict policies

- [ ] **S12.T12** Clock skew: store `device_time` and `server_received_at` separately
  Must know: time handling

- [ ] **S12.T13** Conflict report endpoint and back-office page
  Must know: reporting

- [ ] **S12.T14** Tests: network loss simulation, duplicate upload, out-of-order arrival, each conflict type
  Must know: integration tests, test doubles for network
