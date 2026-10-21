# Stage 25: Marketplace sync (FastAPI + worker)

Where: `services/marketplace-sync`. Prerequisites: stages 17 and 19.

- [ ] **S25.T01** `MarketplaceAdapter` interface and a fake marketplace server (rate limits, 5xx, slowness, duplicate webhooks)
  Must know: fakes with failure injection

- [ ] **S25.T02** Connections and credentials with envelope encryption; never logged
  Must know: envelope encryption, KMS concepts

- [ ] **S25.T03** SKU/category/attribute mapping models and endpoints
  Must know: mapping tables

- [ ] **S25.T04** Stock push from `stock.changed.v1`: coalescing/debounce, safety buffer
  Must know: debouncing, latest-value semantics

- [ ] **S25.T05** Price push from a marketplace price list
  Must know: price lists

- [ ] **S25.T06** Outbound rate limiting: token bucket per tenant+marketplace in Redis, batching, `Retry-After`, circuit breaker
  Must know: token bucket

- [ ] **S25.T07** Order import (webhook or cursor polling), idempotent by marketplace order id → core order via `Idempotency-Key`
  Must know: idempotent import

- [ ] **S25.T08** Oversell conflict policy (cancel/backorder), conflict records, alerts
  Must know: conflict handling

- [ ] **S25.T09** Status push back (shipped/cancelled), marketplace returns
  Must know: two-way sync

- [ ] **S25.T10** Reconciliation job for stock/price differences; DLQ; sync dashboard API
  Must know: reconciliation

- [ ] **S25.T11** Chaos test at 30% errors: eventual match, no duplicate orders, conflicts reported
  Must know: eventual consistency tests

- [ ] **S25.T12** `[EXT]` Channel stock allocation, commissions/payouts to finance; `[OPT]` second adapter
  Must know: allocation rules
