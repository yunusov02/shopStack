# Stage 17: E-commerce channel

Where: `modules/orders`, `/api/storefront/v1/`. Prerequisites: stage 16.

## Storefront API

- [ ] **S17.T01** ADR 0035: orders inside the monolith; ADR 0036 no exact stock quantities online
  Must know: shared stock consistency

- [ ] **S17.T02** Storefront router: tenant by domain, only published products, selling price only, availability buckets
  Must know: public API design

- [ ] **S17.T03** Publishing: `is_online`, online price list (channel), online-visible locations
  Must know: sales channels

- [ ] **S17.T04** Browsing: categories, facet filters, FTS, cursor pagination
  Must know: faceted search

- [ ] **S17.T05** HTTP caching (`ETag`, `Cache-Control`) + Redis cache with invalidation on price/stock change
  Must know: HTTP caching

- [ ] **S17.T06** CORS for the SPA (origins per tenant domain, preflight caching); public API versioning rules; ADR 0037 REST vs RPC vs GraphQL
  Must know: CORS, API versioning

- [ ] **S17.T07** `[EXT]` SEO slugs, sitemap, canonical URLs; `[OPT]` minimal storefront UI
  Must know: SEO basics

## Accounts, cart, checkout

- [ ] **S17.T08** Customer OTP login linked to `Customer` by phone; guest checkout; address book
  Must know: reuse OTP, identity linking

- [ ] **S17.T09** Server-side cart with anonymous token, merge on login, engine recalculation on each change
  Must know: cart merging

- [ ] **S17.T10** Checkout: address, fulfillment (delivery/BOPIS), delivery price (flat until stage 18), promo code, totals with tax snapshots; re-confirm if price changed
  Must know: checkout flow

- [ ] **S17.T11** Order creation: `Idempotency-Key`, reservation with TTL in the same transaction, line snapshots
  Must know: idempotency, reservations

## Payment and lifecycle

- [ ] **S17.T12** `PaymentProvider` interface, Payme/Click adapters + fake, cash on delivery
  Must know: adapters

- [ ] **S17.T13** Payment webhook: signature, idempotency, tiyin amount check, `pending_payment → paid`
  Must know: webhook security

- [ ] **S17.T14** Unpaid order expiry (beat): release reservation, `cancelled`; ADR 0038 late payment handling
  Must know: TTL jobs

- [ ] **S17.T15** Order state machine with transition function and log
  Must know: state machines

- [ ] **S17.T16** Fulfilling location choice; ADR 0039 split shipments; picking/packing in back-office; ADR 0040 when stock is decremented
  Must know: fulfillment

- [ ] **S17.T17** Oversell prevention test: POS + online last item, same lock order
  Must know: concurrency tests

- [ ] **S17.T18** `order.ready_for_delivery.v1`; BOPIS pickup code; customer notifications via Notification service
  Must know: events, commands

- [ ] **S17.T19** Order permissions and audit (`order.fulfill`, `order.cancel`, `order.refund`)
  Must know: permissions

## After-sales

- [ ] **S17.T20** Cancellation rules (customer before picking, staff before shipping): release reservation, refund
  Must know: compensation

- [ ] **S17.T21** Online returns: request → approval → received → refund; restock or write-off; reuse stage 5 refund rules
  Must know: returns flow

- [ ] **S17.T22** Tests: full order lifecycle, cancellation, return, expiry
  Must know: integration tests

- [ ] **S17.T23** `[EXT]` Order history/tracking page; abandoned cart reminders
  Must know: scheduled notifications
