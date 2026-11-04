# Stage 27: Installment sales, consumer credit and gift cards

Where: `modules/credit`. Prerequisites: stages 7 and 26.

## Installments

- [ ] **S27.T01** ADR 0052: markup on price vs interest on balance; rounding rules
  Must know: amortisation math

- [ ] **S27.T02** `InstallmentContract` model + migration (sale, down payment, term, markup, guarantor, documents)
  Must know: contract modelling

- [ ] **S27.T03** Schedule generator (pure function) → `InstallmentPayment` rows; sums exactly (largest remainder); unit tests
  Must know: largest remainder, time zones for due dates

- [ ] **S27.T04** Contract state machine + approval by amount/risk (`credit.contract.approve`)
  Must know: state machines, approvals

- [ ] **S27.T05** Repayment service: full/partial/early, allocation order, POS/bank/balance sources, ledger + journal entries
  Must know: allocation order, ledgers

- [ ] **S27.T06** Overdue job (beat, tenant tz), penalties, `installment.overdue.v1`, reminders, escalation
  Must know: scheduled jobs, events

- [ ] **S27.T07** Exposure limit check with account-row lock; concurrency test
  Must know: row locks

- [ ] **S27.T08** Collections dashboard endpoints and customer statement
  Must know: reporting

- [ ] **S27.T09** Endpoints for contracts, repayments, schedule; tests for the full lifecycle
  Must know: FastAPI, integration tests

- [ ] **S27.T10** `[EXT]` Repossession flow, layaway; `[OPT]` BNPL adapter
  Must know: reversal documents

## Gift cards

- [ ] **S27.T11** `GiftCard` + `GiftCardLedgerEntry` models (liability ledger); code hashed; issue/redeem/expire/breakage
  Must know: liability accounting

- [ ] **S27.T12** Gift card as POS and online payment method; redeem concurrency with row lock; test
  Must know: payment methods, locks

- [ ] **S27.T13** `[EXT]` Physical vs electronic, bulk corporate issue
  Must know: batch generation
