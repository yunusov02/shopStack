# Phase B specs: tenants, staff and catalog

### 7 · A second shop joins

**Files:** `modules/tenancy/*`, `core/tenant_context.py`, `core/db_roles.sql`, `cli/create_tenant.py`, `migrations/versions/0007_tenancy_rls.py`

**Models**

- `tenants`: `id`, `slug UNIQUE`, `name`, `status`, `currency`, `time_zone`, `tax_settings jsonb`, `receipt_settings jsonb`
- `domains`: `id`, `tenant_id`, `host UNIQUE`, `is_primary`
- `locations`: `id`, `tenant_id`, `name`, `kind` (`store`, `warehouse`), `address`
- Every tenant table: policy `USING (tenant_id = current_setting('app.tenant_id')::uuid)`, `ENABLE` + `FORCE`

**Endpoints**

- `GET /api/v1/tenant` (current tenant's settings)
- `GET/POST/PATCH /api/v1/locations`

**Steps**

1. Seed a second tenant. Write the leak test: tenant B's host reads tenant A's sale by ID. It returns `200`; that is the failure to fix.
2. Middleware: `Host` → `domains` → tenant; unknown host → `404`; tenant stored in a `ContextVar`.
3. On transaction begin, `SET LOCAL app.tenant_id`. Global filter with `do_orm_execute` + `with_loader_criteria` on every model with `tenant_id`; a query with no tenant raises.
4. DB roles: `app_user` (no `BYPASSRLS`), `migrator` (owner), `admin_cli` (`BYPASSRLS`). The app connects as `app_user`.
5. Migration enables and forces RLS on every tenant table.
6. `create_tenant --slug --name`, idempotent with `ON CONFLICT (slug)`, run as `admin_cli`.

**Tests**

- `test_tenant_b_cannot_read_tenant_a_sale_returns_404`
- `test_unknown_host_returns_404`
- `test_query_without_tenant_context_raises`
- `test_every_tenant_table_has_forced_rls_policy` (reads `pg_class` and `pg_policies`)
- `test_raw_sql_without_filter_still_isolated_by_rls`
- `test_create_tenant_cli_is_idempotent`

### 8 · Staff log in

**Files:** `modules/accounts/{models,repository,service,router,passwords,tokens,sessions}.py`, `core/middleware.py`, `frontend/apps/back-office/`, `migrations/versions/0008_accounts.py`

**Models**

- `users` (global, no `tenant_id`): `id`, `phone UNIQUE` (E.164), `password_hash`, `is_active`, `last_login_at`
- `memberships`: `id`, `tenant_id`, `user_id`, `status` (`invited`, `active`, `disabled`); `UNIQUE (tenant_id, user_id)`
- `invites`: `id`, `tenant_id`, `phone`, `token_hash`, `expires_at`, `accepted_at`
- `refresh_tokens`: `id`, `user_id`, `tenant_id`, `family_id`, `token_hash`, `expires_at`, `revoked_at`, `replaced_by`
- `audit_log`: `id`, `tenant_id`, `actor_user_id`, `action`, `target_type`, `target_id`, `data jsonb` (insert only)
- `shifts.cashier_name` → `opened_by`; `sales`: add `created_by`

**Endpoints**

- `POST /api/v1/auth/token` `{phone, password}` → access + refresh (POS)
- `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`, `GET /api/v1/me`
- `POST /api/v1/auth/session`, `DELETE /api/v1/auth/session`, `GET /api/v1/sales` (back-office React app, HttpOnly cookie session)
- `POST /api/v1/invites` `{phone}`; `POST /api/v1/invites/{token}/accept` `{password}`

**Steps**

1. `argon2-cffi` hasher; rehash on login when parameters change.
2. Login also requires an active membership in the current tenant.
3. Back-office: session ID in an `HttpOnly; Secure; SameSite=Lax` cookie, data in Redis with a TTL, new ID on login.
4. Access JWT (15 min) with `sub`, `tenant_id`, `exp`, `jti`. Refresh token: random, stored hashed; each use issues a new one; reuse of a replaced token revokes the whole family.
5. Middleware: correlation ID → tenant → auth → error handler. `get_current_user` dependency; token tenant must equal request tenant.
6. One error handler, `/api/v1` router, OpenAPI tags. The back-office React app (login page, sales list) calls the API through a TypeScript client generated from the OpenAPI schema.
7. Audit entries for login, invite, membership change.

**Tests**

- `test_wrong_password_401_does_not_reveal_phone_exists`
- `test_token_from_tenant_a_rejected_on_tenant_b`
- `test_refresh_token_reuse_revokes_family`
- `test_expired_access_token_returns_401`
- `test_backoffice_redirects_to_login_without_session`
- `test_session_id_rotates_on_login`
- `test_invite_token_single_use_and_expires`

### 9 · A cashier can't refund alone

**Files:** `modules/accounts/{permissions,roles,approvals}.py`, `migrations/versions/0009_rbac.py`

**Models**

- `Permission` enum in code: `sale.create`, `sale.refund`, `sale.void`, `sale.discount.manual`, `product.update_price`, `shift.close`, `stock.receive`, `role.manage`
- `roles`: `id`, `tenant_id`, `name`, `is_system`; `role_permissions`: `role_id`, `permission_code`
- `membership_roles`; `membership_locations`
- `manager_pins`: `membership_id`, `pin_hash`, `failed_attempts`, `locked_until`
- `approvals`: `id`, `tenant_id`, `operation`, `target_id`, `amount`, `requested_by`, `approved_by`, `reason`, `token_hash`, `expires_at`, `used_at`

**Endpoints**

- `GET/POST/PATCH /api/v1/roles`; `PUT /api/v1/memberships/{id}/roles`; `PUT /api/v1/memberships/{id}/locations`
- `POST /api/v1/approvals` `{operation, target_id, amount, reason, manager_phone, pin}` → `approval_token`
- Refund, void and large-discount endpoints accept `X-Approval-Token`

**Steps**

1. `require_permission(code)` dependency. Another location's object → `404`, missing permission → `403`.
2. System roles seeded per tenant: owner, manager, cashier.
3. Location scoping in repositories.
4. PIN check with Argon2; 5 failures → locked 15 minutes.
5. Approval token: random, stored hashed, bound to operation, target and amount, valid 2 minutes, consumed with `UPDATE ... WHERE used_at IS NULL RETURNING`.
6. Discounts over 10% and every cashier refund require a token.

**Tests**

- `test_cashier_refund_without_approval_returns_403`
- `test_approval_token_is_single_use`
- `test_approval_token_bound_to_amount_and_target`
- `test_pin_locks_after_five_failures`
- `test_object_in_other_location_returns_404`
- `test_permission_matrix` (parametrized over every route × role)

### 10 · The catalog grows

**Files:** `modules/catalog/{categories,variants,pricing,search,barcodes}.py`, `scripts/seed_catalog.py`, `migrations/versions/0010_catalog.py`

**Models**

- `categories`: `id`, `tenant_id`, `parent_id`, `name`, `path ltree`; `brands`
- `products`: add `category_id`, `brand_id`, `unit` (`pcs`, `kg`, `l`), `is_weighted`, `archived_at`
- `product_variants`: `id`, `tenant_id`, `product_id`, `sku` (`UNIQUE (tenant_id, sku)`), `attributes jsonb`, `archived_at`
- `barcodes`: now point to `variant_id`; add `kind` (`ean13`, `internal`, `scale`)
- `price_lists`: `id`, `tenant_id`, `name`, `kind` (`retail`, `wholesale`)
- `price_list_items`: `price_list_id`, `variant_id`, `location_id NULL`, `price`
- `price_history`: `variant_id`, `price_list_id`, `old_price`, `new_price`, `changed_by`, `changed_at`
- Data migration: one default variant per product; `stock_levels`, `stock_movements`, `sale_lines` move from `product_id` to `variant_id`

**Endpoints**

- CRUD `/api/v1/categories`, `/brands`, `/products`, `/variants`
- `PUT /api/v1/variants/{id}/prices`
- `GET /api/v1/catalog/lookup?barcode=`; `GET /api/v1/catalog/search?q=&location_id=`

**Steps**

1. Seed 5,000 products; record p95 of `ILIKE` search as the baseline.
2. Migration to variants with a backfill and verification query.
3. Price for now: location price, else retail list.
4. Search order barcode → SKU → name; GIN `pg_trgm` index on name.
5. Scale barcodes: prefix `2x`, PLU plus weight or price; EAN-13 check digit validation.
6. A sold product can only be archived.

**Tests**

- `test_barcode_lookup_p95_under_10ms` (benchmark marker)
- `test_scale_barcode_parses_weight_and_price`
- `test_invalid_ean13_check_digit_rejected`
- `test_location_price_overrides_retail`
- `test_price_change_writes_history_and_audit`
- `test_sold_product_can_only_be_archived`
- `test_category_subtree_query`

### 11 · Stock moves between places

**Files:** `modules/inventory/{adjustments,counts,transfers,reservations}.py`, `migrations/versions/0011_stock_operations.py`

**Models**

- `adjustments` + `adjustment_lines`: reason (`damage`, `loss`, `found`, `correction`); status `draft → pending_approval → posted`
- `stock_counts`: `kind` (`full`, `cycle`), status `open → counting → review → posted`, `snapshot_at`; `stock_count_lines`: `variant_id`, `expected_at_snapshot`, `counted`
- `transfers`: `from_location_id`, `to_location_id`, status `requested → approved → picking → shipped → received | cancelled`; `transfer_lines`: `requested`, `shipped`, `received`
- `stock_levels`: add `reserved`, `in_transit`, `min_stock`
- `reservations`: `variant_id`, `location_id`, `quantity`, `source_type`, `source_id`, `expires_at`, `released_at`

**Endpoints**

- `POST /api/v1/adjustments`, `/{id}/submit`, `/{id}/approve`
- `POST /api/v1/stock-counts`, `PUT /{id}/lines`, `/{id}/submit`, `/{id}/approve`
- `POST /api/v1/transfers`, `/{id}/approve`, `/{id}/ship`, `/{id}/receive`
- `GET /api/v1/stock/movements?variant_id=&location_id=&kind=&from=&to=`; `GET /api/v1/stock/low`

**Steps**

1. Posting an adjustment writes movements; value above a tenant threshold needs approval.
2. Count: snapshot expected quantities; variance = counted − (snapshot + movements since snapshot).
3. Ship: decrement the source, increase `in_transit`. Receive: move to the destination, record discrepancies.
4. `available = on_hand − reserved`; reserving locks the row and checks `available`. Held sales reserve.
5. Low stock when `available < min_stock`.

**Tests**

- `test_count_during_sales_variance_correct`
- `test_transfer_partial_receipt_records_discrepancy`
- `test_in_transit_stock_is_not_sellable`
- `test_parallel_reservations_never_exceed_available`
- `test_adjustment_above_threshold_requires_approval`
