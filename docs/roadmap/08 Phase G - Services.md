# Phase G specs: services

Services live in `services/<name>/` with their own Dockerfile, database and migrations. Message contracts live in `contracts/` as JSON Schema.

### 28 · A failing provider doesn't stop sales

**Files:** `modules/integrations/{ports,fakes,resilience,webhooks}.py`, `modules/integrations/adapters/*`, `migrations/versions/0028_integrations.py`

**Models**

- `integration_settings`: `tenant_id`, `provider`, `credentials_encrypted`, `enabled`
- `webhook_endpoints`: `id`, `tenant_id`, `url`, `secret`, `events text[]`, `is_active`
- `webhook_deliveries`: `endpoint_id`, `event_id`, `status`, `attempts`, `next_attempt_at`, `last_response_code`, `last_error`

**Endpoints:** CRUD `/api/v1/webhook-endpoints`; `GET /{id}/deliveries`; `POST /api/v1/webhook-deliveries/{id}/retry`

**Steps**

1. Protocols `PaymentProvider`, `FiscalProvider`, `SmsProvider`, `ReceiptPrinter`; fakes with configurable latency and failure rate.
2. Timeouts on every call; retries with jitter only for idempotent calls.
3. Circuit breaker per tenant and provider, state in Redis (closed, open, half-open).
4. Bulkhead: an `asyncio.Semaphore` per provider.
5. The POS shows card as unavailable while the breaker is open; cash keeps working.
6. Outbound webhooks from outbox events: HMAC-SHA256 with a timestamp, retry schedule, HTTPS only, no redirects, DNS resolved and private ranges blocked.

**Tests**

- `test_breaker_opens_after_failures_then_half_opens`
- `test_card_outage_cash_sale_still_completes`
- `test_bulkhead_limits_concurrency`
- `test_webhook_signature_verifies`
- `test_webhook_to_private_ip_rejected`
- `test_webhook_retries_then_marks_failed`

### 29 · Messages go out reliably

**Files:** `services/notification/{api,worker,models,templates,providers}`, `contracts/commands/notification.send.v1.json`

**Models**

- `templates`: `tenant_id`, `code`, `channel`, `locale`, `body`
- `messages`: `id` (= `message_id`), `tenant_id`, `channel`, `recipient_masked`, `recipient_hash`, `template_code`, `rendered_text`, `status` (`queued`, `sending`, `sent`, `delivered`, `failed`), `attempts`, `provider_message_id`, `error`
- `preferences`: `tenant_id`, `recipient_hash`, `channel`, `opted_out`

**Contracts:** command `notification.send.v1` `{message_id, tenant_id, channel, recipient, template_code, locale, params, priority}`

**Endpoints:** `GET /health`; `GET /v1/messages/{id}`; `POST /v1/providers/{name}/callback`; CRUD `/v1/templates`

**Steps**

1. Exchange `notifications`; priority queue with `x-max-priority`.
2. Consumer inserts the message with `ON CONFLICT DO NOTHING` (deduplication), renders, sends through an adapter.
3. Delayed retries with TTL queues dead-lettering back (1, 5, 30 minutes); then the DLQ; a replay CLI.
4. Token-bucket rate limit per provider; opt-out check; masked logs.
5. Core publishes the command after commit instead of sending SMS itself.

**Tests**

- `test_duplicate_command_sends_once`
- `test_failed_send_retries_with_delay`
- `test_after_max_attempts_goes_to_dlq_and_replays`
- `test_opted_out_recipient_not_sent`
- `test_template_locale_fallback`
- Contract test: the core's command matches the schema

### 30 · New tenants sign up without a developer

**Files:** `services/platform/` (Django: `config/`, `tenants/`, `billing/`, `provisioning/`, `staff/`), core `modules/tenancy/replica_consumer.py`

**Models (Django):** `Tenant`, `Domain`, `Plan` (`limits` JSON), `Subscription` (`status`, `period_start`, `period_end`), `Invoice`, `Payment` (`provider_txn_id` unique), `ProvisioningRun` (`step`, `status`), `Entitlement`, `ImpersonationGrant`; signing keys

**Contracts:** `tenant.created.v1`, `tenant.updated.v1`, `tenant.status_changed.v1`, `tenant.provisioned.v1`, `entitlements.changed.v1`; core internal API `POST /internal/v1/tenants/{id}/provision`

**Endpoints:** React staff-admin app on `admin.<domain>`; `POST /v1/signup`; `POST /v1/billing/payme`; `POST /v1/billing/click`; `GET /.well-known/jwks.json`; `POST /v1/impersonate/{tenant_id}`

**Steps**

1. Django project with a DRF staff admin API; the React staff-admin app (frontend/apps/staff-admin) on admin.<domain>; staff groups, `django-otp` TOTP.
2. Strangler fig: Platform becomes the owner of tenants and domains; the core keeps a replica, upserting by version.
3. Provisioning saga: tenant → core provisions defaults → domain → welcome message; timeouts; compensation marks the run failed and cleans up.
4. Billing: beat creates invoices, `past_due` after the due date, `suspended` after a grace period.
5. Entitlements published as events; the core enforces limits locally.
6. Payme and Click: verify signatures, deduplicate by provider transaction ID, nightly reconciliation.
7. Impersonation: short-lived JWT signed by Platform, verified by the core through JWKS, audited.
8. ADR: DRF vs FastAPI, Django ORM vs SQLAlchemy.

**Tests**

- `test_replica_ignores_older_version`
- `test_saga_compensates_when_core_fails`
- `test_duplicate_payme_callback_is_idempotent`
- `test_unpaid_invoice_past_due_then_suspended`
- `test_suspended_tenant_blocked_in_core`
- `test_impersonation_token_verified_and_audited`
- `test_entitlement_blocks_extra_location`

### 31 · Dashboards don't slow sales

**Files:** `services/analytics/{api,consumer,projections}`, Alembic, `contracts/pacts/`

**Models:** `sales_fact`, `sale_line_fact`, `daily_kpis` (revenue, profit, receipts, average receipt, returns per location and day), `product_stats` (turnover, last sold), `processed_events` (`event_id` PK)

**Endpoints:** `GET /v1/dashboard/today`; `GET /v1/sales/by?dim=location|cashier|category|hour`; `GET /v1/customers/top`; `GET /v1/products/dead-stock`; `GET /v1/products/abc`

**Steps**

1. aiokafka consumer group; commit offsets after the DB commit.
2. One projection handler per event type; `processed_events` row in the same transaction.
3. Late events update past days; refund events correct figures.
4. Replay CLI: truncate projections, reset offsets to earliest.
5. JWT through JWKS; message pacts verified in the core's CI.
6. Daily comparison script against the monolith's reports; switch the dashboard when the diff is zero.

**Tests**

- `test_duplicate_event_projected_once`
- `test_refund_event_corrects_kpis`
- `test_replay_rebuilds_identical_projections`
- `test_late_event_updates_correct_day`

### 32 · Customers order online

**Files:** `modules/storefront/{router,catalog,cart,checkout}.py`, `modules/orders/*`, `migrations/versions/0032_orders.py`

**Models**

- `carts`: `id`, `tenant_id`, `customer_id NULL`, `session_id`; `cart_items`: `variant_id`, `quantity`
- `orders`: `number`, `customer_id`, `status` (`pending_payment`, `paid`, `picking`, `packed`, `ready_for_pickup`, `ready_for_delivery`, `completed`, `cancelled`, `expired`), `fulfillment_location_id`, `delivery_method`, `address jsonb`, totals; `order_lines` with snapshots
- `order_payments`: `provider`, `provider_txn_id UNIQUE`, `amount`, `status`
- `product_variants`: add `is_online`; an online price list

**Endpoints**

- `GET /api/storefront/v1/products?category=&q=&cursor=`; `GET /api/storefront/v1/products/{slug}`
- `GET/POST/PATCH/DELETE /api/storefront/v1/cart/items`
- `POST /api/storefront/v1/checkout/preview`; `POST /api/storefront/v1/orders` (`Idempotency-Key`)
- `POST /api/storefront/v1/payments/payme`, `/click`; `GET /orders/{id}`; `POST /orders/{id}/cancel`
- Back-office: `/orders`, `/orders/{id}/pick`, `/pack`, `/ready`

**Steps**

1. Separate public router with its own CORS and rate limits; the React storefront in frontend/apps/storefront (ADR: SPA with prerendering vs Next.js for SEO).
2. Availability as bands (in stock, few left, out), never exact counts; `ETag` and Redis caching.
3. Cart merges on login; checkout reprices with the engine and flags changes that need confirmation.
4. Order: reserve stock with a 15-minute TTL, snapshot lines.
5. Payment webhook marks paid idempotently; beat expires unpaid orders.
6. Fulfilment flow, pick up in store, cancellation and returns.
7. `order.ready_for_delivery.v1` through the outbox.

**Tests**

- `test_last_item_pos_and_online_only_one_wins`
- `test_unpaid_order_expires_and_releases_stock`
- `test_duplicate_payment_webhook_is_idempotent`
- `test_checkout_price_change_requires_confirmation`
- `test_cart_merges_on_login`
- `test_storefront_hides_exact_stock`

### 33 · Orders are delivered with live tracking

**Files:** `services/delivery/{api,zones,quotes,dispatch,tracking,cash}`, `frontend/apps/courier/`

**Models:** `zones` (`polygon geometry`, fee rules), `quotes` (`point`, `fee`, `eta`, `expires_at`), `deliveries` (`order_id`, `status`, `courier_id`, `version`), `couriers`, `delivery_offers` (`expires_at`, `response`), `courier_cash_entries` (`collected`, `handed_over`)

**Contracts:** in `order.ready_for_delivery.v1`; out `delivery.accepted.v1`, `delivery.delivered.v1`, `delivery.failed.v1`, `courier_cash.handed_over.v1`

**Endpoints:** `POST /v1/quotes`; courier `GET /v1/offers`, `POST /v1/offers/{id}/accept`, `POST /v1/deliveries/{id}/status`, `POST /v1/location`, `POST /v1/deliveries/{id}/handover` `{otp}`; `WS /v1/track/{delivery_id}`; back-office zones CRUD

**Steps**

1. `ST_Contains` picks the zone; the quote's snapshot is used at checkout.
2. Consumer creates the delivery; `GEOSEARCH` finds the nearest courier; 30-second offer, then the next courier.
3. Atomic accept: `UPDATE ... WHERE id = :id AND status = 'offered' AND version = :v`.
4. Positions into Redis GEO; pub/sub fans out to WebSocket clients.
5. Heartbeat timeout → reassignment. Handover OTP sent to the customer. Cash ledger per courier.
6. Failure saga: the core consumes `delivery.failed.v1`, refunds through the payment adapter and returns stock. ADR on choreography.
7. Pact tests; Playwright end-to-end from order to delivered.

**Tests**

- `test_two_couriers_accept_one_wins`
- `test_offer_timeout_moves_to_next_courier`
- `test_address_outside_zones_gets_no_quote`
- `test_expired_quote_rejected`
- `test_failed_delivery_refunds_and_restocks`
- `test_offline_courier_reassigned`
- `test_handover_requires_otp`

### 34 · One sale is followed across services

**Files:** `deploy/observability/{otel-collector,prometheus,alerts,loki}.yaml`, `deploy/observability/grafana/dashboards/*.json`, `core/telemetry.py` per service, `docs/slo.md`, `docs/runbooks/*`, `docs/postmortems/*`

**Steps**

1. OpenTelemetry SDK and auto-instrumentation for FastAPI, Django, SQLAlchemy, httpx, Celery; manual propagation through Kafka and RabbitMQ headers and the event envelope.
2. Metrics: RED per endpoint; `sales_completed_total`, outbox backlog, consumer lag, DLQ size, breaker state.
3. Logs to Loki with `trace_id`; dashboards per service and one for the business.
4. SLO: 99.9% successful sale completions and p95 under 300 ms over 28 days; multi-window burn-rate alerts with runbook links.
5. Synthetic checks: health endpoints and a scripted test sale on staging.
6. Chaos drills: Kafka down, slow Postgres, provider outage; one postmortem each.

**Done when:** one trace shows POS → core → outbox → Kafka → Analytics; a chaos drill fires an alert that links a runbook; dashboards live in git.

### 35 · Deploys stop being manual

**Files:** `deploy/helm/_lib/`, `deploy/helm/<service>/`, `deploy/k8s/{ingress,cert-manager,network-policies}/`, `.github/workflows/cd.yml`

**Steps**

1. k3d cluster; a library chart (Deployment, Service, HPA, PDB) and per-service values.
2. ADR: CloudNativePG and Strimzi operators vs managed services.
3. Wildcard ingress with the edge routing table; cert-manager wildcard certificate via DNS-01; default-deny NetworkPolicies.
4. Sealed Secrets or External Secrets; requests and limits; probes; migrations as a pre-upgrade Job.
5. Rollout strategy ADR; rehearsed `helm rollback`; one column rename done as expand/contract across three releases.
6. HPA for the core; KEDA on RabbitMQ queue length and Kafka lag; one active beat and relay through a Lease.
7. CD: build changed services, deploy to staging, manual approval, production.
8. Restore drill on a fresh cluster.

**Done when:** zero failed requests during a rolling deploy under Locust; rollback in under 5 minutes; a restored cluster passes reconciliation; a NetworkPolicy blocks Analytics from the core database.

### 36 · Audit records can't be tampered with

**Files:** `services/audit/` (Django)

**Models:** `AuditRecord`: `tenant_id`, `seq`, `occurred_at`, `actor`, `action`, `target_type`, `target_id`, `data`, `prev_hash`, `hash`; `UNIQUE (tenant_id, seq)`; `ChainHead` per tenant

**Contracts:** in `audit.recorded.v1` from the core, Platform and Delivery

**Steps**

1. Kafka consumer; lock the tenant's chain head, `hash = sha256(prev_hash + canonical_json)`, append.
2. The app's DB role has no `UPDATE` or `DELETE`.
3. Nightly verifier recomputes every chain.
4. DRF search API with django-filter; read-only screens in the React staff-admin app.
5. Producers switch from the local `audit_log` once the service is verified.

**Tests**

- `test_tampered_record_detected_by_verifier`
- `test_update_denied_by_db_role`
- `test_duplicate_event_appended_once`
- `test_chain_contiguous_under_parallel_events`

### 37 · Large files skip the monolith

**Files:** `services/media/{api,worker,storage,processing}`

**Models:** `assets`: `tenant_id`, `owner_type`, `owner_id`, `status` (`pending`, `ready`, `rejected`), `content_type`, `size`, `key`, `variants jsonb`

**Endpoints:** `POST /v1/uploads` `{content_type, size, owner}` → presigned PUT + `asset_id`; `POST /v1/uploads/{id}/confirm`; `GET /v1/assets/{id}`

**Steps**

1. Presigned URL with a content-length range, valid 5 minutes.
2. Worker sniffs magic bytes and rejects mismatches.
3. Pillow in a process pool: 200 px and 600 px WebP thumbnails, EXIF stripped.
4. `media.asset.ready.v1`; the core stores `asset_id` on the product.
5. Orphan cleanup; quotas from entitlements.

**Tests**

- `test_fake_extension_rejected`
- `test_oversize_upload_rejected`
- `test_exif_is_stripped`
- `test_orphans_are_deleted`
- `test_quota_exceeded_returns_409`

### 38 · Suppliers confirm POs themselves

**Files:** `services/supplier_portal/` (Django + DRF API; React UI in frontend/apps/supplier-portal)

**Models:** `SupplierAccount`, `SupplierUser` (phone, TOTP), `SupplierLink` (`tenant_id`, `core_supplier_id`), `PurchaseOrderReplica` (`status`, `lines`, `version`), `Asn`, `Invoice`

**Contracts:** in `purchase_order.sent.v1`, `purchase_order.updated.v1`; out core internal API `POST /internal/v1/purchase-orders/{id}/confirm`, `/asn`, `/invoices` with `Idempotency-Key` and a service token

**Steps**

1. Own identity; a tenant links a supplier by inviting a phone number.
2. Replica consumer by version.
3. React pages: PO list, confirm, ASN form; DRF token API for larger suppliers.
4. Every query filtered through `SupplierLink`.

**Tests**

- `test_supplier_sees_only_linked_tenants`
- `test_confirm_command_is_idempotent`
- `test_core_rejects_command_for_unlinked_supplier`
- `test_replica_ignores_older_version`

### 39 · Marketplace stock and prices stay in sync

**Files:** `services/marketplace_sync/{api,worker,adapters/fake,adapters/uzum}`

**Models:** `connections` (`credentials_encrypted`, `status`), `sku_mappings`, `push_jobs` (`kind`, `variant_id`, `desired_value`, `status`, `attempts`), `imported_orders` (`external_order_id` unique per connection), `conflicts`

**Contracts:** in `stock.changed.v1`, `price_list.changed.v1`; out order commands to the core's internal API

**Steps**

1. Coalesce pushes per variant (the latest value wins).
2. Token bucket per connection; honour `Retry-After`; circuit breaker.
3. Order import by webhook or polling, deduplicated.
4. When the core can't reserve stock: record a conflict and request cancellation.
5. A fake marketplace with 30% errors and `429`s.

**Tests**

- `test_rapid_stock_changes_coalesce_into_one_push`
- `test_429_respects_retry_after`
- `test_order_imported_once`
- `test_oversell_creates_conflict_and_cancel_request`
