# Phase E specs: business domain

### 20 · Goods arrive from suppliers

**Files:** `modules/procurement/*`, `modules/procurement/costing.py`, `modules/payables/*`, `migrations/versions/0020_procurement.py`

**Models**

- `suppliers`: `id`, `tenant_id`, `name`, `tin`, `phone`, `payment_terms_days`, `is_active`
- `purchase_orders`: `id`, `tenant_id`, `number`, `supplier_id`, `location_id`, `status`, `total`, `expected_at`, `approved_by`, `approved_at`; `po_lines`: `po_id`, `variant_id`, `quantity`, `unit_cost`, `received_qty`
- `goods_receipts` + `goods_receipt_lines`: `po_line_id`, `quantity`, `unit_cost`, `batch_no`, `expiry_date`
- `stock_levels`: add `avg_cost numeric(14,4)`
- `supplier_returns` + lines; `supplier_invoices`: `supplier_id`, `receipt_id`, `amount`, `due_date`, `status`; `supplier_payments`
- `supplier_ledger_entries`: `supplier_id`, `kind` (`invoice`, `payment`, `return`), signed `amount`

**Endpoints**

- CRUD `/api/v1/suppliers`
- `POST /api/v1/purchase-orders`, `PATCH /{id}/lines`, `/{id}/submit`, `/{id}/approve`, `/{id}/send`, `/{id}/cancel`
- `POST /api/v1/purchase-orders/{id}/receipts` `{lines}`
- `POST /api/v1/supplier-returns`; `POST /api/v1/supplier-invoices/{id}/payments`; `GET /api/v1/suppliers/{id}/statement`

**Steps**

1. Transition table for PO states; anything else → `409`.
2. Approval threshold from tenant settings; approving needs `purchase.approve`.
3. Receipt: lock PO lines and stock rows; set `partially_received` or `received`; flag excess.
4. WAC under the row lock: `new_avg = (on_hand × avg + qty × cost) / (on_hand + qty)`.
5. Sale completion now snapshots `avg_cost`; remove the temporary `/stock/receive` endpoint.
6. Invoice from receipt; payments; statement as a running balance over the ledger.

**Tests**

- `test_po_invalid_transition_returns_409`
- `test_po_above_threshold_requires_approval`
- `test_partial_receipt_sets_partially_received`
- `test_parallel_receipts_wac_correct`
- `test_sale_after_receipt_snapshots_avg_cost`
- `test_supplier_return_reduces_stock_and_payable`
- `test_supplier_balance_equals_ledger_sum`

### 21 · Promotions apply automatically

**Files:** `modules/pricing/{engine,rules,models,repository,router}.py`, `tests/unit/pricing/*`, `tests/vectors/pricing/*.json`

**Models**

- `promotions`: `id`, `tenant_id`, `name`, `kind` (`percent`, `fixed`, `fixed_price`, `buy_x_get_y`, `free_item`), `conditions jsonb` (variants, categories, brands, locations, minimum amount, weekdays, time window), `benefit jsonb`, `priority`, `stackable`, `starts_at`, `ends_at`, `usage_limit`, `used_count`
- `coupons`: `id`, `promotion_id`, `code` (`UNIQUE (tenant_id, code)`), `usage_limit`, `used_count`; `coupon_redemptions`: `coupon_id`, `sale_id`
- `sale_lines`: add `applied_promotions jsonb`

**Endpoints**

- CRUD `/api/v1/promotions`; `POST /api/v1/coupons/generate` `{promotion_id, count}`
- `POST /api/v1/sales/{id}/coupons` `{code}`; `DELETE /api/v1/sales/{id}/coupons/{code}`
- `POST /api/v1/pricing/preview` `{lines}`

**Steps**

1. `price(cart, rules, now, tz) -> PricedCart` with no I/O.
2. Base price by the resolution order (ADR); the customer group step plugs in at slice 22.
3. Filter rules by conditions; order by priority, then ID.
4. Stacking: among non-stackable rules pick the best for the customer.
5. Buy X Get Y frees the cheapest items; receipt discounts allocated by largest remainder.
6. The sale service loads rules and calls the engine on every line change.
7. Coupon use at completion: `UPDATE ... SET used_count = used_count + 1 WHERE used_count < usage_limit RETURNING`; returned on void.
8. Store test vectors as JSON so the POS engine (slice 25) runs the same cases.

**Tests**

- Property tests: `test_total_never_negative`, `test_discount_never_exceeds_line_total`, `test_allocation_sums_exactly`, `test_same_input_same_output`
- `test_happy_hour_uses_tenant_time_zone`
- `test_buy_2_get_1_frees_cheapest`
- `test_non_stackable_picks_best_for_customer`
- `test_coupon_limit_holds_under_parallel_use`
- `test_void_returns_coupon_use`

### 22 · Regular customers earn and owe

**Files:** `modules/customers/{models,repository,service,router,loyalty,credit}.py`, `migrations/versions/0022_customers.py`

**Models**

- `customers`: `id`, `tenant_id`, `phone`, `name`, `group_id`, `birthday`; `UNIQUE (tenant_id, phone)`
- `customer_groups`: `id`, `name`, `price_list_id`, `discount_percent`
- `loyalty_entries`: `customer_id`, `kind` (`earn`, `spend`, `expire`, `reverse`), `points`, `sale_id`, `expires_at`
- `store_credit_entries`: `customer_id`, `kind` (`topup`, `spend`, `refund`), `amount`, `reference_id`
- `customer_accounts`: `customer_id` PK, `credit_limit`, `balance`; `credit_entries`: `kind` (`charge`, `repayment`), `amount`, `sale_id`

**Endpoints**

- CRUD `/api/v1/customers`; `GET /api/v1/customers/{id}/history`; `GET /api/v1/customers/{id}/statement`
- `POST /api/v1/sales/{id}/customer` `{customer_id}`
- `POST /api/v1/customers/{id}/store-credit/topup`; `POST /api/v1/customers/{id}/repayments`
- Payment methods `points`, `store_credit`, `credit`

**Steps**

1. Earn points at completion by the tenant's rule; spend them as a payment; reverse proportionally on refund.
2. Group price joins the pricing resolution order.
3. Credit sale: lock `customer_accounts` with `FOR UPDATE`; `balance + amount <= credit_limit` or `409`.
4. Repayments and a statement with a running balance.

**Tests**

- `test_points_earned_and_reversed_on_refund`
- `test_points_balance_equals_ledger_sum`
- `test_parallel_credit_sales_cannot_exceed_limit`
- `test_store_credit_payment_reduces_balance`
- `test_group_price_applied_in_resolution_order`
- `test_same_phone_409_in_tenant_allowed_in_other_tenant`

### 23 · The owner sees profit

**Files:** `modules/finance/{models,repository,service,router,reports}.py`, `scripts/reconcile_payments.py`, `migrations/versions/0023_finance.py`

**Models**

- `payment_transactions`: `id`, `tenant_id`, `location_id`, `shift_id`, `kind` (`sale`, `refund`, `supplier_payment`, `customer_repayment`, `expense`, `cash_in`, `cash_out`), `method`, signed `amount`, `reference_type`, `reference_id`, `occurred_at`
- `expense_categories`; `expenses`: `category_id`, `location_id`, `amount`, `method`, `note`, `paid_at`

**Endpoints**

- CRUD `/api/v1/expenses`, `/api/v1/expense-categories`
- `GET /api/v1/finance/cash-balance?location_id=`
- `GET /api/v1/reports/profit?from=&to=&location_id=`; `GET /api/v1/reports/ar-aging`; `GET /api/v1/reports/ap-aging`

**Steps**

1. Every money movement writes a `payment_transactions` row inside its own transaction; add this to the existing services.
2. Cash balance = sum of cash transactions per location.
3. Revenue net of VAT; COGS = quantity × cost snapshot, minus restocked refunds; gross profit.
4. Aging buckets with `CASE` on days past `due_date`.
5. `reconcile_payments.py`: transactions vs sales, refunds and payments.

**Tests**

- `test_every_completed_sale_has_payment_transactions`
- `test_cash_balance_matches_shift_expected_cash`
- `test_gross_profit_for_known_dataset`
- `test_refund_reduces_revenue_and_cogs`
- `test_ar_aging_buckets`

### 24 · A new cashier is hired

**Files:** `modules/hr/*`, `migrations/versions/0024_hr.py`

**Models:** `employees`: `id`, `tenant_id`, `user_id NULL`, `full_name`, `phone`, `position`, `location_id`, `status` (`candidate`, `interview`, `offer`, `hired`, `rejected`, `terminated`), `hired_at`

**Endpoints:** `POST /api/v1/employees`; `POST /api/v1/employees/{id}/transition` `{to}`; `GET /api/v1/employees`

**Steps**

1. Transition table; invalid moves → `409`.
2. On `hired`, in the same transaction: invite the user if needed, create the membership, the role mapped from the position, and location access.
3. On `terminated`, disable the membership.

**Tests**

- `test_hire_creates_membership_and_role_once`
- `test_invalid_transition_returns_409`
- `test_terminated_employee_cannot_log_in`
