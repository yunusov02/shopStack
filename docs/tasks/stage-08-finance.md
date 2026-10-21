# Stage 8: Finance

Where: `modules/finance`. Prerequisites: stage 7. Done when the gross profit report built from cost snapshots matches a manual calculation.

## Ledger and cash `[CORE]`

- [ ] **S8.T01** `PaymentTransaction` model + migration (append-only): type (`sale | refund | supplier_payment | customer_payment | expense | cash_in | cash_out`), method, amount, location, shift, reference, `occurred_at`
  Must know: unified transaction ledger

- [ ] **S8.T02** Hook every money event (sales, refunds, payables, customer payments, shift cash) into the ledger in the same transaction
  Must know: cross-module writes in one UoW

- [ ] **S8.T03** Cash balance per location and per shift derived from the ledger; endpoint
  Must know: aggregate queries

- [ ] **S8.T04** `ExpenseCategory` and `Expense` models + migration; service and endpoints (`finance.manage`)
  Must know: CRUD

- [ ] **S8.T05** Tests: ledger completeness (every money event has a transaction), cash balance
  Must know: integration tests

## Reports `[CORE]`

- [ ] **S8.T06** Revenue report by period and location (from completed sales)
  Must know: `date_trunc`, time zone conversion for display

- [ ] **S8.T07** COGS and gross profit from `SaleLine.unit_cost` snapshots; by period, location, category
  Must know: snapshot-based reporting, `GROUP BY ROLLUP` optional

- [ ] **S8.T08** Accounts receivable and payable aging report (0–30, 31–60, 61–90, 90+)
  Must know: `CASE` buckets, date math

- [ ] **S8.T09** Report endpoints with `report.view`, export CSV with `report.export`
  Must know: streaming responses

- [ ] **S8.T10** Test: gross profit report equals a hand-computed fixture
  Must know: fixtures with known numbers

## Extensions

- [ ] **S8.T11** `[EXT]` Cash flow report (inflows/outflows by category and period)
  Must know: report queries

- [ ] **S8.T12** `[EXT]` `JournalEntry` + `JournalLine` models + migration; deferred constraint trigger enforcing debit = credit per entry
  Must know: deferred constraints, triggers

- [ ] **S8.T13** `[EXT]` Posting from sale, refund, receipt, payment into journal entries; reversing entries for corrections
  Must know: double-entry basics

- [ ] **S8.T14** `[EXT]` `FiscalPeriod` model + closing; writes into a closed period rejected by a trigger
  Must know: period locking
