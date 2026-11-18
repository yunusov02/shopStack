# Phase A specs: one store, one till

One seeded tenant and location, no auth. Until slice 10, `product_id` is the stock unit; variants replace it there.

### 1 · Cashier sells a product by barcode

**Files:** `main.py`, `core/settings.py`, `core/db.py`, `core/uow.py`, `core/errors.py`, `modules/catalog/*`, `modules/sales/*`, `scripts/seed.py`, `docker-compose.yml`, `migrations/versions/0001_catalog_sales.py`

**Models**

- `products`: `id`, `tenant_id`, `name text`, `price numeric(14,2) CHECK (price >= 0)`
- `barcodes`: `id`, `tenant_id`, `product_id → products`, `code text`; `UNIQUE (tenant_id, code)`
- `sales`: `id`, `tenant_id`, `location_id`, `status` (`draft`, `completed`), `total numeric(14,2)`, `completed_at`
- `sale_lines`: `id`, `sale_id → sales`, `product_id`, `name_snapshot`, `unit_price`, `quantity numeric(12,3)`, `line_total`

**Endpoints**

- `GET /health`
- `POST /api/v1/sales` → `201` draft sale
- `POST /api/v1/sales/{id}/lines` `{barcode, quantity = 1}` → sale with lines and total
- `POST /api/v1/sales/{id}/complete` → completed sale
- `GET /api/v1/sales/{id}`

**Steps**

1. `create_app()` with a lifespan that creates the engine and disposes it on shutdown.
2. `get_uow` dependency: one session per request; `commit()` explicit, rollback on exception.
3. Models and migration; `scripts/seed.py` creates one tenant, one location and 20 products with barcodes.
4. Repositories: `ProductRepository.get_by_barcode`, `SaleRepository.add/get`.
5. `SaleService.add_line`: barcode → product (`404` if missing), snapshot name and price, recompute the total in `Decimal`.
6. `SaleService.complete`: only `draft`, at least one line; set `completed_at`.
7. Compose: `postgres:16` with a healthcheck; run the app locally with `uv run`.

**Tests**

- `test_sell_two_products_by_barcode_total_is_sum`
- `test_unknown_barcode_returns_404_and_sale_unchanged`
- `test_complete_empty_sale_returns_409`
- `test_add_line_to_completed_sale_returns_409`
- `test_price_change_after_sale_keeps_snapshot`
- unit: `test_line_total_decimal_rounding`

### 2 · Stock goes down and never below zero

**Files:** `modules/inventory/*`, `migrations/versions/0002_stock.py`, `scripts/reconcile_stock.py`

**Models**

- `stock_levels`: `tenant_id`, `location_id`, `product_id`, `on_hand numeric(12,3) CHECK (on_hand >= 0)`; PK `(tenant_id, location_id, product_id)`
- `stock_movements`: `id`, `tenant_id`, `location_id`, `product_id`, `kind` (`receive`, `sale`, `adjustment`), `quantity` (signed), `reference_type`, `reference_id`; the repository has no update or delete

**Endpoints**

- `POST /api/v1/stock/receive` `{location_id, product_id, quantity}` (temporary, replaced by procurement in slice 20)
- `GET /api/v1/stock?location_id=`

**Steps**

1. `InventoryService.receive`: movement + upsert of the level in one transaction.
2. Write the race test first: two sessions complete sales of the last unit with `asyncio.gather`. Watch it fail.
3. In `complete()`: sort line product IDs, `SELECT ... FOR UPDATE` the stock rows in that order, check, decrement, write `sale` movements, then mark the sale completed. One Unit of Work.
4. Not enough stock → `409` with the products and shortfalls.
5. `reconcile_stock.py`: compare `on_hand` with the sum of movements per row.

**Tests**

- `test_parallel_sales_of_last_unit_one_succeeds_one_409`
- `test_failed_completion_writes_no_movements`
- `test_opposite_line_order_does_not_deadlock`
- `test_on_hand_equals_sum_of_movements_after_random_operations`

### 3 · A retried request doesn't sell twice

**Files:** `core/idempotency.py`, `migrations/versions/0003_idempotency.py`

**Models**

- `idempotency_keys`: `tenant_id`, `key`, `request_hash`, `status` (`in_progress`, `done`), `response_code`, `response_body jsonb`, `expires_at`; PK `(tenant_id, key)`

**Endpoints:** `POST /api/v1/sales/{id}/complete` now requires the `Idempotency-Key` header.

**Steps**

1. Missing header → `400`.
2. `INSERT ... ON CONFLICT DO NOTHING`. Inserted → run the operation. Not inserted → read the row: different hash → `409`; `in_progress` → `409` with "retry later"; `done` → replay the stored response.
3. Store the response in the same transaction as the sale.
4. `scripts/purge_idempotency_keys.py` for expired rows (a beat job in slice 18).

**Tests**

- `test_same_key_twice_returns_same_response_one_sale`
- `test_parallel_same_key_writes_one_sale`
- `test_same_key_different_body_returns_409`
- `test_missing_key_returns_400`

### 4 · Pay, get change, print a receipt

**Files:** `modules/sales/tax.py`, `modules/sales/payments.py`, `modules/sales/receipts.py`, `templates/receipt.txt`, `migrations/versions/0004_payments_receipts.py`

**Models**

- `products`: add `tax_rate numeric(5,2)`; tenant setting `prices_include_tax bool`
- `sale_lines`: add `tax_rate`, `tax_amount`, `discount_amount`
- `sale_payments`: `id`, `sale_id`, `method` (`cash`, `card`), `amount`, `tendered`, `change`, `terminal_ref`
- `receipt_counters`: `tenant_id`, `location_id`, `last_number`; PK `(tenant_id, location_id)`
- `sales`: add `receipt_number`, `public_token`, `held_until`, status `held`

**Endpoints**

- `POST /api/v1/sales/{id}/lines/{line_id}/discount` `{percent}` (maximum 10% for now)
- `POST /api/v1/sales/{id}/payments` `{method, amount, tendered?}`; `DELETE /api/v1/sales/{id}/payments/{payment_id}`
- `POST /api/v1/sales/{id}/hold`, `POST /api/v1/sales/{id}/resume`
- `GET /api/v1/sales/{id}/receipt` (printer text); `GET /r/{public_token}` (public receipt page)

**Steps**

1. `tax.py` as pure functions: included and added VAT, one rounding rule (ADR).
2. Payments; `complete` requires `sum(payments) == total`; cash computes change.
3. Receipt number at completion: lock the counter row, increment. Measure completions per second with and without it.
4. Receipt text at 42 columns with a QR code linking to `/r/{public_token}`.
5. Hold: `held` with `held_until`; `resume` returns to `draft` unless expired.

**Tests**

- `test_split_payment_cash_and_card_completes`
- `test_underpaid_sale_cannot_complete`
- `test_cash_change_is_tendered_minus_due`
- `test_vat_included_and_added_cases` (table-driven)
- `test_receipt_numbers_gapless_under_20_parallel_completions`
- `test_expired_hold_cannot_resume`

### 5 · Open and close a shift

**Files:** `modules/shifts/*`, `migrations/versions/0005_shifts.py`

**Models**

- `shifts`: `id`, `tenant_id`, `location_id`, `cashier_name` (a user ID from slice 8), `status` (`open`, `closed`), `opened_at`, `closed_at`, `opening_cash`, `counted_cash`, `expected_cash`, `z_report jsonb`; partial unique index on `location_id WHERE status = 'open'`
- `cash_movements`: `id`, `shift_id`, `kind` (`in`, `out`), `amount`, `reason`
- `sales`: add `shift_id`

**Endpoints**

- `POST /api/v1/shifts` `{location_id, opening_cash}`
- `POST /api/v1/shifts/{id}/cash-movements` `{kind, amount, reason}`
- `GET /api/v1/shifts/{id}/x-report`
- `POST /api/v1/shifts/{id}/close` `{counted_cash}` → Z report

**Steps**

1. A sale is created only inside an open shift of its location.
2. Expected cash = opening + cash sales − cash refunds + cash in − cash out.
3. The X report computes live; the Z report freezes the figures into `z_report` at close.

**Tests**

- `test_second_open_shift_same_location_returns_409`
- `test_sale_without_open_shift_returns_409`
- `test_expected_cash_formula`
- `test_closed_shift_rejects_sales_and_cash_movements`
- `test_z_report_totals_equal_sum_of_sales`

### 6 · Refund, void, exchange

**Files:** `modules/sales/refunds.py`, `migrations/versions/0006_refunds.py`

**Models**

- `refunds`: `id`, `tenant_id`, `original_sale_id`, `shift_id`, `total`, `exchange_sale_id`
- `refund_lines`: `refund_id`, `sale_line_id`, `quantity`, `amount`, `restock bool`
- `refund_payments`: `refund_id`, `method`, `amount`
- `sales`: add `voided_at`, `void_reason`; `stock_movements.kind` adds `refund`, `write_off`

**Endpoints**

- `POST /api/v1/sales/{id}/refunds` `{lines: [{sale_line_id, quantity, restock}]}`
- `POST /api/v1/sales/{id}/void` `{reason}`
- `POST /api/v1/sales/{id}/exchange` `{refund_lines, new_sale_id}`
- `GET /api/v1/sales/{id}/receipt?duplicate=true`

**Steps**

1. Lock the original sale row; refundable = sold − already refunded, per line.
2. Refund amounts include the line's share of discounts (largest remainder).
3. Restocked items write `refund` movements; damaged ones write `write_off`.
4. Money goes back by the original method; cash refunds reduce the shift's expected cash.
5. Void only within the same open shift; it reverses stock and payments.
6. Exchange = refund + new sale in one transaction; the difference is paid or refunded.

**Tests**

- `test_parallel_refunds_cannot_exceed_sold_quantity`
- `test_partial_refund_amounts_sum_exactly`
- `test_restock_true_returns_stock_false_writes_off`
- `test_void_in_other_shift_returns_409`
- `test_exchange_difference_paid_and_refunded`
- `test_duplicate_receipt_is_marked`
