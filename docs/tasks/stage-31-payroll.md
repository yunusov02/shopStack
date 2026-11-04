# Stage 31: HR and payroll

Where: `modules/hr`, `modules/payroll`. Prerequisites: stages 11 and 26.

- [ ] **S31.T01** Schedules, attendance (POS check-in/out linked to shift), overtime, absence types, leave ledger
  Must know: time tracking, ledgers

- [ ] **S31.T02** `Compensation` model with effective dates: salary, hourly, commission rules, bonuses
  Must know: effective dating

- [ ] **S31.T03** `PayrollRuleSet` versioned (income tax, social contributions) with validity dates
  Must know: versioned rules

- [ ] **S31.T04** Payroll calculation as a pure function; unit tests with known cases; idempotent recalculation
  Must know: pure functions, Decimal

- [ ] **S31.T05** `PayrollRun` state machine `draft → calculated → approved → paid → posted`; journal entries on approval
  Must know: state machines, posting

- [ ] **S31.T06** Payslips (PDF via stage 32), bank export file, `payroll.posted.v1`
  Must know: document generation

- [ ] **S31.T07** Privacy: separate permission, masked logs, no raw salaries in events
  Must know: PII handling

- [ ] **S31.T08** Endpoints and tests: a month with overtime, commission, leave; identical rerun
  Must know: integration tests

- [ ] **S31.T09** `[EXT]` KPI bonuses, shortage deductions, employee self-service; `[OPT]` Django extraction
  Must know: policies
