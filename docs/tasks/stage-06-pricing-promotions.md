# Stage 6: Pricing and promotions engine

Where: `modules/pricing`. Prerequisites: stage 5. Done when the result is deterministic for any cart and the property tests are green.

## Price resolution `[CORE]`

- [ ] **S6.T01** ADR 0018: price resolution order (customer price → location price → customer group → base retail)
  Must know: resolution order, precedence rules

- [ ] **S6.T02** `CustomerPrice` and `CustomerGroupPrice` models + migration (customer module arrives in stage 7; create the tables now with nullable FKs or defer the FK)
  Must know: forward dependencies between modules

- [ ] **S6.T03** `resolve_price()` extended per the ADR; unit tests per level
  Must know: pure functions, parametrized tests

## Promotion model `[CORE]`

- [ ] **S6.T04** `Promotion` model + migration: name, `conditions` (JSONB: products, categories, brands, locations, customer groups, min qty/amount, date range, weekdays, time of day), `benefit` (JSONB: percent, fixed, fixed price, free item), `priority`, `is_exclusive`, `max_per_line`, `is_active`
  Must know: JSONB schema design, Pydantic models for JSONB

- [ ] **S6.T05** Pydantic schemas for `conditions` and `benefit` with validation; stored as validated JSON
  Must know: discriminated unions in Pydantic v2

- [ ] **S6.T06** Promotion repository, service (CRUD, activate/deactivate, `promotion.manage` permission), endpoints
  Must know: CRUD, permission dependency

## Engine `[CORE]`

- [ ] **S6.T07** Engine input/output types: `CartInput` (lines with variant, qty, base price, category, brand), `Context` (location, customer group, local datetime), `PricingResult` (per-line price, discounts, applied promotions)
  Must know: dataclasses / Pydantic for value objects, Decimal

- [ ] **S6.T08** Condition matcher: pure function `matches(promotion, line, context) -> bool`; time-of-day and weekday in the tenant time zone
  Must know: `zoneinfo`, pure functions

- [ ] **S6.T09** Benefit appliers: percentage, fixed amount, fixed price, category/brand discount; each a strategy function
  Must know: strategy pattern, Decimal rounding

- [ ] **S6.T10** Buy X Get Y: group eligible lines, cheapest free, repeated application per receipt
  Must know: grouping and sorting, greedy allocation

- [ ] **S6.T11** Stacking rules: sort by priority, exclusive stops, `max_per_line`; deterministic order (priority, then id)
  Must know: determinism, stable sorting

- [ ] **S6.T12** Receipt-level discount allocation across lines with largest remainder; sum equals the discount exactly
  Must know: largest remainder method, Decimal quantize

- [ ] **S6.T13** `PricingEngine.price(cart, promotions, context) -> PricingResult` as a pure function (no DB access); loader in the service layer fetches promotions
  Must know: separating IO from logic

- [ ] **S6.T14** Property-based tests with `hypothesis`: total never negative, line sums equal total, idempotent re-run, order of lines doesn't change totals
  Must know: hypothesis strategies, invariants

- [ ] **S6.T15** Unit tests for each benefit and the stacking rules, including happy hour at the time zone boundary
  Must know: parametrize, time zone edge cases

## Coupons and promo codes `[CORE]`

- [ ] **S6.T16** `Coupon` (single-use unique codes, batch generated) and `PromoCode` (shared code, `total_limit`, `per_customer_limit`, `used`) models + migration
  Must know: code generation, counters

- [ ] **S6.T17** Promo code consumption: atomic `UPDATE promo_codes SET used = used + 1 WHERE code = :c AND used < total_limit RETURNING ...` on sale completion; release on void
  Must know: atomic UPDATE ... WHERE, compensation on void

- [ ] **S6.T18** `PromoCodeUsage` per customer for per-customer limits; unique constraint
  Must know: usage tracking

- [ ] **S6.T19** Endpoints: generate coupons, promo code CRUD, apply code to a cart (validation only; consumption at completion)
  Must know: FastAPI, two-phase apply/consume

- [ ] **S6.T20** Concurrency test: parallel completions with the same promo code never exceed the limit
  Must know: concurrency tests

## Integration with sales `[CORE]`

- [ ] **S6.T21** `CartService` calls the engine on every change; applied promotions stored as snapshots on `SaleLine.promotions`
  Must know: snapshots, cross-module calls

- [ ] **S6.T22** Partial refund uses the allocated line discounts (from stage 5) so amounts are correct
  Must know: refund math with discounts

- [ ] **S6.T23** Tests: end-to-end sale with promotions and a promo code, partial refund amounts
  Must know: integration tests

- [ ] **S6.T24** `[EXT]` Promotion preview endpoint: simulate a cart against active promotions without a sale
  Must know: reusing the engine
