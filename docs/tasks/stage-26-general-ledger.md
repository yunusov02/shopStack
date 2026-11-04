# Stage 26: General ledger and accounting

Where: `modules/accounting`. Prerequisites: stage 8.

## Chart of accounts and posting

- [ ] **S26.T01** `Account` model + migration: tree per tenant, code, type, currency, active; template seeding per tax regime; delete forbidden when entries exist
  Must know: chart of accounts, account types

- [ ] **S26.T02** `JournalEntry` + `JournalLine` models + migration; deferred constraint trigger debit = credit; append-only; reversing entry service
  Must know: double-entry, deferred constraints

- [ ] **S26.T03** `PostingRule` model + migration: document type × event → account mappings as data
  Must know: configuration as data

- [ ] **S26.T04** Posting engine: pure function `(document, rules) -> JournalEntry`; unit tests per document type
  Must know: pure functions, Decimal

- [ ] **S26.T05** Post inside the document transaction (sale, refund, receipt, payment, adjustment); ADR 0050 sync posting vs events
  Must know: transaction boundaries

- [ ] **S26.T06** Backfill command for existing documents; assert ledger revenue == stage 8 report
  Must know: batch backfill, reconciliation

- [ ] **S26.T07** Sub-ledger reconciliation job (AR, AP, inventory value, cash) with differences report
  Must know: reconciliation queries

## Periods and reports

- [ ] **S26.T08** `FiscalPeriod` model + state machine; DB trigger rejecting posts into closed periods; reopen with permission + audit
  Must know: period locking, triggers

- [ ] **S26.T09** Reports: trial balance, account ledger, P&L, balance sheet (period, location, cost centre)
  Must know: financial statements, SQL aggregation

- [ ] **S26.T10** Year-end closing service (close P&L accounts to retained earnings)
  Must know: closing entries

- [ ] **S26.T11** VAT accounts and VAT return report
  Must know: VAT accounting

- [ ] **S26.T12** Property-based test: any document sequence keeps the trial balance balanced
  Must know: hypothesis

## Multi-currency, banks, assets

- [ ] **S26.T13** `Currency`, `ExchangeRate` (validity dates) models; document and base amounts; FX gain/loss entries
  Must know: multi-currency accounting

- [ ] **S26.T14** `BankAccount`, `BankStatementLine` models; statement import (ADR 0051 format); matching service and unmatched report
  Must know: bank reconciliation

- [ ] **S26.T15** `[EXT]` Fixed assets register, depreciation methods, monthly run, disposal
  Must know: depreciation

- [ ] **S26.T16** `[EXT]` Budgets and budget vs actual; cost centres and dimensions on lines
  Must know: analytical dimensions

- [ ] **S26.T17** `[OPT]` 1C journal export
  Must know: export formats
