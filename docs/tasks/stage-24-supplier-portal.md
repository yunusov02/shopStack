# Stage 24: Supplier portal (Django + DRF + HTMX)

Where: `services/supplier-portal`. Prerequisites: stages 15 and 23.

- [ ] **S24.T01** Django service skeleton on `suppliers.<domain>`; Django templates + HTMX; ADR 0048 Django templates vs Jinja2
  Must know: Django templates, HTMX

- [ ] **S24.T02** Custom user model `SupplierUser` (phone E.164) + `SupplierAccount` before first migration
  Must know: `AUTH_USER_MODEL`

- [ ] **S24.T03** Login: password (Argon2 hasher) and OTP backend; sessions, CSRF, rate limiting
  Must know: authentication backends

- [ ] **S24.T04** Linking flow: tenant invite → accept → `SupplierLink` → `supplier.linked.v1`
  Must know: cross-service invites

- [ ] **S24.T05** Link-scoped manager/queryset (fail closed, 404), shared by template views and DRF views
  Must know: custom managers

- [ ] **S24.T06** PO replica consumer (`purchase_order.*`), version check; only supplier-visible fields
  Must know: read models

- [ ] **S24.T07** Confirm/propose-change commands to monolith internal API (service token, `Idempotency-Key`); rejection shown
  Must know: service commands

- [ ] **S24.T08** ASN model + flow; pre-filled goods receipt in monolith
  Must know: ASN

- [ ] **S24.T09** Invoice upload via Media → draft payables invoice; payment status from events
  Must know: presigned uploads from Django

- [ ] **S24.T10** DRF API for supplier ERPs: API keys (hashed, revocable), throttling, spectacular
  Must know: API key auth

- [ ] **S24.T11** Isolation matrix tests (2 tenants × 2 suppliers), Pact contracts, audit via outbox
  Must know: test matrices

- [ ] **S24.T12** `[EXT]` Three-way match, price proposals, account roles + 2FA (ADR 0049); `[OPT]` PO messaging
  Must know: three-way matching
