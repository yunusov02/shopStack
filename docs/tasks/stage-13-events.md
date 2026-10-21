# Stage 13: Events and preparing for extraction

Prerequisites: stage 12. Done when the extraction conditions are met.

- [ ] **S13.T01** `import-linter` contracts: modules may import only `core` and declared interfaces; CI check
  Must know: import-linter, layered contracts

- [ ] **S13.T02** Remove cross-module JOINs and FKs toward future services (analytics, notification); replace with ids and events
  Must know: data ownership, decoupling

- [ ] **S13.T03** Event envelope dataclass: `event_id`, `type`, `version`, `tenant_id`, `occurred_at`, `correlation_id`, `payload`; Pydantic schemas per event type
  Must know: schema versioning

- [ ] **S13.T04** Domain events: `sale.completed.v1`, `sale.refunded.v1`, `stock.changed.v1`, `stock.low.v1`, `order.ready_for_delivery.v1`, `customer.created.v1` emitted from services
  Must know: domain events

- [ ] **S13.T05** ADR 0027: sync vs async boundary after `SaleCompleted`
  Must know: consistency boundaries

- [ ] **S13.T06** ADR 0028: delivery semantics (at-most/at-least/exactly-once), outbox + inbox
  Must know: delivery guarantees

- [ ] **S13.T07** `Outbox` model + migration; services write events in the same transaction
  Must know: transactional outbox

- [ ] **S13.T08** Outbox relay process: `SELECT ... FOR UPDATE SKIP LOCKED`, publish, mark sent; backoff on failure
  Must know: `SKIP LOCKED`, relay loop

- [ ] **S13.T09** Kafka (KRaft) in Compose; producer with key `tenant_id`; topics per aggregate
  Must know: Kafka basics, partitioning by key

- [ ] **S13.T10** Inbox table and idempotent consumer base class (`event_id` unique) for in-monolith consumers
  Must know: inbox pattern

- [ ] **S13.T11** Schema compatibility rules documented: additive changes vs new version
  Must know: backward compatibility

- [ ] **S13.T12** Correlation ID propagated HTTP → outbox → Kafka headers → consumer; structlog JSON logging
  Must know: context propagation, structlog

- [ ] **S13.T13** CI builds several images (api, worker, relay)
  Must know: CI matrix builds

- [ ] **S13.T14** Tests: outbox written with the document, relay publishes once, consumer dedups
  Must know: Kafka in tests (Testcontainers)
