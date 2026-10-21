# Stage 18: Delivery service (FastAPI)

Where: `services/delivery`, `courier-app/`. Prerequisites: stage 17.

- [ ] **S18.T01** Service skeleton with PostGIS and Redis; Dockerfile, CI
  Must know: PostGIS, GeoAlchemy2

- [ ] **S18.T02** `Courier` model, statuses; courier app login (OTP) with device binding
  Must know: OTP reuse, device tokens

- [ ] **S18.T03** Delivery zones as polygons per location; point-in-polygon check
  Must know: `ST_Contains`, polygons

- [ ] **S18.T04** Quote API: by zone/distance, minimum order, free threshold; quote id + TTL; storefront stores quote snapshot
  Must know: quote design

- [ ] **S18.T05** Delivery created from `order.ready_for_delivery.v1` (idempotent by order id)
  Must know: idempotent consumers

- [ ] **S18.T06** Dispatch: nearest available courier (Redis GEO), offer with timeout, next courier
  Must know: Redis GEO, timeouts

- [ ] **S18.T07** Atomic acceptance `UPDATE ... WHERE status='offered'`; concurrency test
  Must know: atomic UPDATE

- [ ] **S18.T08** Delivery state machine + `delivery.status_changed.v1`
  Must know: state machines, events

- [ ] **S18.T09** Courier location updates: throttled, Redis GEO current, sampled history in PostGIS
  Must know: throttling, geo storage

- [ ] **S18.T10** ADR 0041 SSE vs WebSocket vs long polling; WebSocket tracking with Redis pub/sub, reconnect handling
  Must know: WebSocket, pub/sub

- [ ] **S18.T11** Courier offline mid-delivery: timeout and reassignment
  Must know: timeouts, reassignment

- [ ] **S18.T12** Handover OTP via Notification; cash on delivery: courier cash ledger, handover, `courier_cash.handed_over.v1`
  Must know: ledgers, events

- [ ] **S18.T13** Failure saga (choreography): `delivery.failed.v1` → core cancels/refunds → stock back on return; idempotent steps; ADR 0042 choreography vs orchestration
  Must know: choreography saga

- [ ] **S18.T14** Pact contract tests (events, quote API); Playwright e2e order → delivery → confirmation
  Must know: Pact, Playwright

- [ ] **S18.T15** `[EXT]` Route batching, ETA, proof-of-delivery photo (stage 23)
  Must know: routing basics
