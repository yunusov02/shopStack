# Stage 7: Customers and loyalty

Where: `modules/customers`. Prerequisites: stage 6. Done when parallel sales never break the credit limit and points/balance are correct after a refund.

## Customers `[CORE]`

- [ ] **S7.T01** `Customer` model + migration: `tenant_id`, phone unique per tenant, name, `group_id`, `birthday`, notes
  Must know: unique per tenant, nullable date

- [ ] **S7.T02** `CustomerGroup` model + migration: retail, wholesale, VIP; default groups seeded per tenant
  Must know: seed data

- [ ] **S7.T03** Customer repository, service (create, update, search by phone/name), endpoints (`customer.read`, `customer.manage`)
  Must know: CRUD, trigram search reuse

- [ ] **S7.T04** Attach customer to a sale: `Sale.customer_id`, cart endpoint; customer group feeds the pricing engine context
  Must know: cross-module integration

- [ ] **S7.T05** Purchase history endpoint per customer (sales, refunds) with cursor pagination
  Must know: keyset pagination

- [ ] **S7.T06** Tests: uniqueness, search, attach to sale, group pricing
  Must know: integration tests

## Loyalty points `[CORE]`

- [ ] **S7.T07** `PointsLedgerEntry` model + migration (append-only): customer, type (`earn | spend | expire | cancel`), points, reference, `expires_at`
  Must know: ledger pattern

- [ ] **S7.T08** `EarningRule` model + migration: points per amount, per group, per category, active period
  Must know: rule tables

- [ ] **S7.T09** `LoyaltyService`: earn on completion (same transaction), spend as payment method or discount, cancel on refund proportionally; balance = sum of entries
  Must know: proportional reversal, Decimal/int points

- [ ] **S7.T10** Points as a payment method in `PaymentService` (`points` method, conversion rate)
  Must know: payment method extension

- [ ] **S7.T11** Endpoints: balance, statement, earning rules CRUD
  Must know: FastAPI

- [ ] **S7.T12** Tests: earn/spend/cancel on refund, balance correctness
  Must know: integration tests

## Store credit and customer debt `[CORE]`

- [ ] **S7.T13** `CustomerAccount` model + migration: customer, `balance` (store credit), `debt`, `credit_limit`; `BalanceLedgerEntry` and `DebtLedgerEntry` append-only
  Must know: balance column + ledger pattern, reconciliation

- [ ] **S7.T14** `StoreCreditService`: top-up, pay with balance at POS, refund to balance; balance updated in the same transaction as the entry
  Must know: dual-write consistency within one transaction

- [ ] **S7.T15** `CreditService.sell_on_credit(sale, amount)`: lock the account row (`with_for_update`), check `debt + amount <= credit_limit`, write entry; `customer.credit.manage` for limit changes
  Must know: account-level lock, read-check-write race

- [ ] **S7.T16** Debt repayment (cash/card/bank) and customer statement endpoint
  Must know: ledger reports

- [ ] **S7.T17** Reconciliation job: `balance == SUM(entries)` and `debt == SUM(entries)` per account
  Must know: reconciliation queries

- [ ] **S7.T18** Concurrency test: two terminals selling on credit in parallel never exceed the limit
  Must know: concurrency tests

- [ ] **S7.T19** Tests: top-up, pay with balance, refund to balance, repayment, statement
  Must know: integration tests

## Extensions

- [ ] **S7.T20** `[EXT]` Cashback to balance as a promotion benefit type
  Must know: engine extension

- [ ] **S7.T21** `[EXT]` Birthday promotion job (Celery beat after stage 9, tenant time zone)
  Must know: scheduled jobs, time zones

- [ ] **S7.T22** `[EXT]` Automatic points expiry job writing `expire` entries
  Must know: idempotent batch jobs
