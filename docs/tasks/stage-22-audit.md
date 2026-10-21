# Stage 22: Audit service (Django + DRF)

Where: `services/audit`. Prerequisites: stage 15.

- [ ] **S22.T01** Django service skeleton (same standards as Platform)
  Must know: Django, DRF

- [ ] **S22.T02** Kafka consumer as management command; graceful shutdown; commit after DB commit
  Must know: management commands, signals (SIGTERM)

- [ ] **S22.T03** `audit.recorded.v1` envelope and monolith emission via outbox (same transaction as the sensitive operation)
  Must know: outbox reuse

- [ ] **S22.T04** Idempotent ingestion (`event_id` unique), `bulk_create` batches with measurements
  Must know: bulk inserts

- [ ] **S22.T05** Append-only: role without UPDATE/DELETE + trigger, both in `RunSQL`
  Must know: `RunSQL`, triggers

- [ ] **S22.T06** Monthly partitioning via `RunSQL`; beat task for future partitions
  Must know: partitioning in Django

- [ ] **S22.T07** Immutable model: `save()` only new, `delete()`/queryset updates forbidden; ADR 0046 why both ORM and DB
  Must know: Django model overrides

- [ ] **S22.T08** Hash chain per tenant (`prev_hash`, `hash` over canonical JSON); verification beat job; tamper test
  Must know: hashing, canonical JSON

- [ ] **S22.T09** DRF `ReadOnlyModelViewSet`, django-filter, `CursorPagination`, drf-spectacular
  Must know: DRF read-only APIs

- [ ] **S22.T10** JWKS auth class; tenant isolation (fail closed, 404)
  Must know: custom DRF authentication

- [ ] **S22.T11** Read-only admin, fast changelist, staff 2FA, separate host
  Must know: admin customization

- [ ] **S22.T12** Connect Platform and Delivery audit; strangler fig from monolith audit table
  Must know: parallel run

- [ ] **S22.T13** `[EXT]` Daily root hash anchoring, signed exports, retention; `[OPT]` crypto-shredding ADR
  Must know: signing, retention
