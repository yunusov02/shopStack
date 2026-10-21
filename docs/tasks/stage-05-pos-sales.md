# Stage 5: POS sales

Where: `modules/sales`. Prerequisites: stage 4. Done when, under load, stock never goes negative and a sale is never written twice; partial refunds, exchanges and voids work.

## Cart `[CORE]`

- [ ] **S5.T01** ADR 0013: server-side cart (`Sale` in `draft`) vs client cart
  Must know: hold/resume requirements, state on server

- [ ] **S5.T02** `Sale` + `SaleLine` models + migration: status (`draft → held → completed / voided`), location, cashier, customer (nullable), totals; line snapshots: `unit_price`, `unit_cost`, `tax_rate`, `tax_amount`, `discount_amount`, `promotions` (JSONB)
  Must know: snapshot columns, Decimal, JSONB

- [ ] **S5.T03** `SaleRepository` and `CartService`: create draft, add line by barcode/SKU/variant id, change quantity (weighted supported), remove line, recalc totals
  Must know: Decimal arithmetic, catalog lookups

- [ ] **S5.T04** Manual item line (`sale.manual_item` permission): no variant, no stock effect, name and price given
  Must know: nullable FKs, permission checks

- [ ] **S5.T05** Manual discount (line and receipt): `sale.discount.manual`, max percentage from tenant settings; above limit requires approval token (S5.T27)
  Must know: percentage limits, Decimal rounding

- [ ] **S5.T06** ADR 0014: tax rounding (line vs receipt level), VAT included vs added
  Must know: VAT math, rounding modes (`ROUND_HALF_UP`)

- [ ] **S5.T07** Tax calculation pure function per the ADR; snapshot on lines; unit tests with edge cases
  Must know: pure functions, Decimal quantize

- [ ] **S5.T08** Hold and resume: `held` status, `held_until`, ADR 0015 whether a hold reserves stock; expiry job
  Must know: reservations (S3.T24), TTL jobs

- [ ] **S5.T09** Cart endpoints: create, add/update/remove line, apply manual discount, hold, resume, list held
  Must know: FastAPI, permissions

- [ ] **S5.T10** Tests: cart math, weighted lines, discount limits, hold/resume
  Must know: Decimal assertions, parametrize

## Payment `[CORE]`

- [ ] **S5.T11** `Payment` model + migration: sale, method (`cash | card | balance | credit | points`), amount, tendered, change, terminal reference, status
  Must know: payment modelling, Decimal

- [ ] **S5.T12** `PaymentService.add_payment(sale, ...)`: cash with change, card with reference; split payments; `sum(payments) == total` check on completion
  Must know: split payment math

- [ ] **S5.T13** Payment endpoints: add payment, remove payment (draft only)
  Must know: FastAPI

- [ ] **S5.T14** Tests: split payment, overpayment with change, mismatch rejected
  Must know: integration tests

## Completion `[CORE]`

- [ ] **S5.T15** `ReceiptCounter` model + migration: per location, `last_number`; gapless allocation with `with_for_update`
  Must know: gapless sequences, row locks vs Postgres sequences

- [ ] **S5.T16** `IdempotencyKey` model + migration: key, tenant, request hash, response, `expires_at`; `idempotent` dependency returning the stored response or `409` on different payload
  Must know: idempotency keys, request hashing, TTL

- [ ] **S5.T17** `SaleService.complete(sale_id, idempotency_key)`: validate → lock stock rows ordered by `variant_id` → decrement → movements → payments check → snapshots → receipt number → `completed`; one transaction
  Must know: lock ordering, one ACID transaction, snapshots

- [ ] **S5.T18** Bundle/kit handling on completion: bundle deducts components; kit deducts kit stock
  Must know: composition from S2.T14–T15

- [ ] **S5.T19** Complete endpoint (`sale.create`) with `Idempotency-Key` header required
  Must know: header dependencies, 409 semantics

- [ ] **S5.T20** Tests: completion decrements stock, idempotent retry returns same receipt, gapless numbers under parallel completions
  Must know: concurrency tests

## Receipt `[CORE]`

- [ ] **S5.T21** Receipt renderer: text template for printers (fixed width) and PDF (library by ADR 0016); snapshot stored
  Must know: Jinja2 text templates, PDF generation basics

- [ ] **S5.T22** Electronic receipt: public token URL and QR code image; endpoint `GET /r/{token}`
  Must know: unguessable tokens, QR generation

- [ ] **S5.T23** Duplicate receipt: marked "DUPLICATE", audit log entry
  Must know: audit helper

- [ ] **S5.T24** Tests: receipt rendering, token access, duplicate audit
  Must know: snapshot testing

## Post-sale `[CORE]`

- [ ] **S5.T25** `SaleService.void(sale)`: draft → cancelled; completed within the same shift → full reversal (stock back, payments reversed), `sale.void`, approval token, audit
  Must know: reversal documents, same-shift rule

- [ ] **S5.T26** `Refund` + lines models + migration: original sale, quantities per line, restock vs write-off, refund payments by method
  Must know: refund modelling

- [ ] **S5.T27** `RefundService`: cannot exceed sold − already refunded (lock the original sale row), restock movements or damaged adjustment, refund to method rules, `sale.refund`, audit
  Must know: row lock on original sale, concurrency on parallel refunds

- [ ] **S5.T28** `Exchange`: refund + new sale linked by `exchange_id`; difference paid or refunded
  Must know: linked documents

- [ ] **S5.T29** Endpoints: void, refund, exchange
  Must know: FastAPI, permissions

- [ ] **S5.T30** Tests: partial refund limits, parallel refunds, exchange difference, void after shift rejected
  Must know: concurrency tests

- [ ] **S5.T31** `[EXT]` Return without receipt by tenant policy (price from current list, flagged, audit)
  Must know: policy settings

## Manager approval `[CORE]`

- [ ] **S5.T32** Manager PIN: hashed (Argon2), attempt limit, set/change endpoint
  Must know: hashing, attempt counters

- [ ] **S5.T33** `ApprovalRequest` model + migration: operation type, amount, requested_by, approved_by, token hash, `expires_at` (2 min), `used_at`
  Must know: single-use tokens

- [ ] **S5.T34** `ApprovalService`: request → verify PIN on same terminal → issue token bound to operation+amount; consume on use; audit who/why
  Must know: step-up authorization, token binding

- [ ] **S5.T35** Approval endpoints; wire into manual discount, void, refund
  Must know: dependency composition

- [ ] **S5.T36** Tests: token single-use, binding mismatch rejected, expiry
  Must know: time freezing

- [ ] **S5.T37** `[EXT]` Remote approval over WebSocket (after stage 9)
  Must know: FastAPI WebSocket, Redis pub/sub

## Shifts and cash drawer `[CORE]`

- [ ] **S5.T38** `Shift` model + migration: location, terminal, cashier, opened/closed at, opening cash, expected, counted, difference
  Must know: shift lifecycle

- [ ] **S5.T39** `CashMovement` model + migration: shift, type (`cash_in | cash_out | sale | refund`), amount; append-only
  Must know: ledger pattern

- [ ] **S5.T40** `ShiftService`: open, cash in/out, close with counted cash and difference; sales require an open shift
  Must know: invariants across modules

- [ ] **S5.T41** X report (current shift) and Z report (closed shift) endpoints
  Must know: aggregate queries

- [ ] **S5.T42** Tests: shift open/close, difference, sales without shift rejected
  Must know: integration tests

## Concurrency and load `[CORE]`

- [ ] **S5.T43** Reproduce a deadlock on purpose (two sales locking variants in opposite order), then fix with ordered locking; retry on `DeadlockDetected`
  Must know: deadlocks, `pg_locks`, retry decorators

- [ ] **S5.T44** Optimistic locking variant: `version` column on `StockLevel`, compare-and-set; measure vs `with_for_update` under load; keep one (ADR 0017)
  Must know: optimistic vs pessimistic locking

- [ ] **S5.T45** Isolation level lab: scripts reproducing lost update, non-repeatable read, phantom read at `READ COMMITTED` and `REPEATABLE READ`; `SERIALIZABLE` with retry; README notes
  Must know: isolation levels, anomalies, serialization failures

- [ ] **S5.T46** ACID notes on the sale transaction in README: atomicity (savepoint around payment adapter), consistency (constraints), isolation (lab), durability (WAL, `synchronous_commit`)
  Must know: ACID, savepoints, WAL

- [ ] **S5.T47** Locust scenario: 50 parallel cashiers completing sales on overlapping variants; assert no negative stock and no duplicate receipts; results in README
  Must know: Locust, load testing, assertions after load
