# Phase H specs: ERP

All of this stays in the monolith; every posting happens inside the transaction of the document that causes it.

### 40 · The accountant closes a month

**Files:** `modules/accounting/{models,posting,rules,periods,reports,bank}.py`, `migrations/versions/0040_gl.py`

**Models**

- `accounts`: `id`, `tenant_id`, `code`, `name`, `type` (`asset`, `liability`, `equity`, `revenue`, `expense`), `parent_id`, `currency`
- `journal_entries`: `id`, `tenant_id`, `date`, `period_id`, `source_type`, `source_id`, `memo`, `reversal_of`
- `journal_lines`: `entry_id`, `account_id`, `debit`, `credit`, `currency`, `amount_fx`, `rate`
- `periods`: `start`, `end`, `status` (`open`, `closed`); `posting_rules`: `source_type`, `template jsonb`
- `bank_statements` + `bank_statement_lines`; `reconciliations`

**Endpoints**

- CRUD `/api/v1/accounts`; `GET /api/v1/journal`; `POST /api/v1/journal` (manual entry)
- `POST /api/v1/periods/{id}/close`
- `GET /api/v1/reports/trial-balance`, `/pnl`, `/balance-sheet`
- `POST /api/v1/bank-statements` (CSV import); `POST /api/v1/bank-reconciliations/match`

**Steps**

1. Seed a default chart of accounts per tenant.
2. Posting service called inside sale, refund, receipt, supplier payment and expense transactions, mapped by rules.
3. Deferred constraint trigger: debit = credit per entry at commit.
4. Trigger rejects inserts dated in a closed period; corrections only by reversal entries.
5. Trial balance, P&L, balance sheet; multi-currency through a rates table.
6. Bank import and matching by amount, date and reference.
7. AR, AP and inventory sub-ledgers reconcile to their GL control accounts.

**Tests**

- `test_unbalanced_entry_rejected_at_commit`
- `test_closed_period_rejects_raw_sql_insert`
- `test_every_sale_posts_balanced_entry`
- `test_reversal_nets_to_zero`
- `test_pnl_matches_finance_gross_profit`
- `test_inventory_subledger_equals_gl_control`

### 41 · Customers pay in installments

**Files:** `modules/credit/*`, `migrations/versions/0041_installments_gift_cards.py`

**Models**

- `installment_contracts`: `customer_id`, `sale_id`, `principal`, `down_payment`, `term_months`, `rate`, `status`
- `installment_schedule`: `contract_id`, `due_date`, `principal_due`, `interest_due`, `paid`, `status`; `installment_payments`; `penalties`
- `gift_cards`: `code_hash`, `initial`, `balance`, `status`, `expires_at`; `gift_card_entries`

**Endpoints:** `POST /api/v1/installments`; `GET /api/v1/installments/{id}/schedule`; `POST /api/v1/installments/{id}/payments`; `POST /api/v1/gift-cards`; payment method `gift_card`

**Steps**

1. Schedule with equal payments in `Decimal`; the last payment absorbs rounding.
2. Payment allocation: penalties → interest → principal.
3. Nightly overdue job, penalties once per period, `installment.overdue.v1` to Notification.
4. Gift card sale is a liability; redemption locks the card row and recognises revenue.
5. GL postings for all of it.

**Tests**

- `test_schedule_sums_to_principal_plus_interest`
- `test_payment_allocation_order`
- `test_penalty_applied_once_per_period`
- `test_parallel_gift_card_redemptions_cannot_overspend`
- `test_credit_ledger_equals_gl_account`

### 42 · The shop assembles its own products

**Files:** `modules/production/*`, `migrations/versions/0042_production.py`

**Models:** `boms` (`variant_id`, `version`, `is_active`), `bom_lines` (`component_variant_id`, `quantity`, `scrap_percent`), `work_orders` (`planned → released → in_progress → completed | cancelled`), `wo_consumptions`, `wo_outputs`; movement kinds `produce_consume`, `produce_output`

**Endpoints:** CRUD `/api/v1/boms`; `POST /api/v1/work-orders`, `/{id}/release`, `/{id}/consume`, `/{id}/complete`

**Steps**

1. Explode multi-level BOMs with a recursive CTE; reject cycles.
2. Release reserves components; consumption moves cost to WIP.
3. Completion: finished stock at materials + overhead rate.
4. GL: inventory → WIP → finished goods.

**Tests**

- `test_bom_cycle_rejected`
- `test_multilevel_explosion_quantities`
- `test_completion_cost_is_components_plus_overhead`
- `test_stock_reconciles_after_production`
- `test_wip_is_zero_after_completion`

### 43 · The system suggests what to buy

**Files:** `modules/planning/{demand,forecast,replenishment}.py`, `migrations/versions/0043_planning.py`

**Models:** `demand_history` (location, variant, day, quantity), `forecasts` (`horizon_day`, `quantity`, `method`), `replenishment_params` (`lead_time_days`, `service_level`, `min`, `max`), `suggestions` (`kind` `po` or `transfer`, quantity, `status`)

**Endpoints:** `POST /api/v1/planning/run`; `GET /api/v1/planning/suggestions`; `POST /api/v1/planning/suggestions/{id}/accept`

**Steps**

1. Nightly job builds demand history from the sales summary.
2. Simple exponential smoothing per series.
3. Safety stock = z × σ × √lead time; reorder point = mean daily demand × lead time + safety stock.
4. Suggested quantity = max − (available + on order + in transit); accepting creates a draft PO or transfer.
5. `replenishment.suggested.v1`; 8-week backtest with WAPE.

**Tests**

- `test_reorder_point_formula`
- `test_on_order_quantity_not_suggested_again`
- `test_accept_creates_draft_po`
- `test_backtest_reports_wape`

### 44 · Approvals become configurable

**Files:** `modules/workflow/{engine,definitions,approvals,numbering}.py`, `migrations/versions/0044_workflow.py`

**Models:** `workflow_definitions` (`document_type`, `states`, `transitions`, `version`), `approval_policies` (`rules jsonb`: thresholds → roles and steps), `approval_requests`, `approval_steps`, `number_sequences` (`document_type`, `prefix`, `next_value`, `reset_policy`)

**Endpoints:** CRUD `/api/v1/approval-policies`; `GET /api/v1/approvals/inbox`; `POST /api/v1/approvals/{id}/approve`, `/reject`

**Steps**

1. Generic `transition(document, to, actor)` with guards and hooks.
2. Approval steps generated from the tenant's policy.
3. Migrate sales, POs, transfers and adjustments one at a time; their old tests must pass unchanged.
4. Numbering service replaces `receipt_counters` and PO numbers.

**Tests**

- All earlier state-machine tests pass unchanged
- `test_policy_change_applies_without_deploy`
- `test_two_step_approval_order`
- `test_numbering_gapless_per_document_type`

### 45 · Salaries are calculated

**Files:** `modules/payroll/*`, `migrations/versions/0045_payroll.py`

**Models:** `attendance`, `leaves`, `compensation` (`kind` salary, hourly or commission; `effective_from`, `effective_to`), `payroll_runs` (`draft → calculated → approved → posted → paid`), `payslips` (`gross`, `deductions jsonb`, `net`), `tax_rates` table

**Endpoints:** `POST /api/v1/attendance/check-in`, `/check-out`; `POST /api/v1/payroll-runs`, `/{id}/calculate`, `/{id}/approve`, `/{id}/post`; `GET /api/v1/payroll-runs/{id}/bank-file`

**Steps**

1. Effective-dated compensation lookup with proration.
2. Hours and overtime from attendance; commission from cashier sales.
3. Taxes and contributions from the rates table, never hardcoded.
4. Posting to the GL; approved runs are immutable.

**Tests**

- `test_mid_month_salary_change_prorated`
- `test_draft_rerun_is_identical`
- `test_commission_from_sales`
- `test_payroll_entries_balanced`
- Property test: net = gross − deductions

### 46 · Documents render from templates

**Files:** `modules/documents/{templates,render,pdf}.py`, `modules/reporting/{engine,schedules,exports}.py`, `migrations/versions/0046_documents_reports.py`

**Models:** `document_templates` (`kind`, `locale`, `body`, `version`), `report_definitions` (`query_ref`, params schema), `report_schedules` (`cron`, `channel`, recipients), `report_runs`

**Endpoints:** CRUD `/api/v1/document-templates`; `GET /api/v1/documents/{kind}/{id}.pdf?locale=`; `POST /api/v1/reports/{name}/run`; CRUD `/api/v1/report-schedules`; `GET /api/v1/exports/{id}`

**Steps**

1. Sandboxed Jinja environment for tenant templates; WeasyPrint rendering in a worker.
2. Babel formats for uz-Latn, uz-Cyrl and ru.
3. Report engine: allowlisted queries with typed parameters.
4. Exports streamed from a generator with `StreamingResponse`.
5. Beat runs schedules and sends results through Notification.

**Tests**

- `test_template_sandbox_blocks_internals`
- `test_pdf_renders_in_three_locales`
- `test_streamed_export_memory_is_constant`
- `test_schedule_runs_and_delivers`

### 47 · One tenant runs several companies

**Files:** `modules/companies/*`, `migrations/versions/0047_companies.py`

**Models:** `companies` (`legal_name`, `tin`, `currency`); `locations` and `journal_entries`: add `company_id`; `intercompany_transactions` (`from_company`, `to_company`, source document, matched entries)

**Endpoints:** CRUD `/api/v1/companies`; `GET /api/v1/reports/consolidated?from=&to=`

**Steps**

1. Every posting carries `company_id`.
2. A transfer between companies creates mirrored due-to and due-from entries.
3. Consolidated report sums companies and eliminates intercompany balances and revenue.

**Tests**

- `test_intercompany_transfer_creates_mirrored_entries`
- `test_each_company_trial_balance_balances`
- `test_consolidation_eliminates_intercompany`
