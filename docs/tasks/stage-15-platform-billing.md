# Stage 15: Platform and Billing service (Django + DRF)

Where: `services/platform`. Prerequisites: stage 14.

## Foundation

- [ ] **S15.T01** Django project, split settings, own Postgres, DRF, Dockerfile, CI; pytest-django, factory_boy, Testcontainers
  Must know: Django project layout, DRF, pytest-django

- [ ] **S15.T02** Apps with a service layer (`services.py`), no logic in views/serializers
  Must know: Django apps, service layer

- [ ] **S15.T03** Celery with Django (RabbitMQ)
  Must know: Celery + Django integration

## Admin and staff

- [ ] **S15.T04** Custom `AdminSite` on a separate host; platform staff user model; Groups and Permissions; ADR 0029 vs monolith RBAC
  Must know: Django admin, auth groups

- [ ] **S15.T05** Mandatory TOTP 2FA for staff (django-otp or own)
  Must know: TOTP in Django

- [ ] **S15.T06** Admin actions: suspend tenant, change plan; MRR dashboard view
  Must know: admin actions, custom views

- [ ] **S15.T07** Audit: admin log + own audit table
  Must know: `LogEntry`, custom audit

## Tenant registry ownership

- [ ] **S15.T08** `Tenant`, `Domain`, `Plan` models in Django; ADR 0030 strangler fig for tenant ownership
  Must know: strangler fig

- [ ] **S15.T09** Outbox + Kafka producer in Django; events `tenant.*`, `domain.changed`, `entitlements.changed`
  Must know: outbox in Django ORM

- [ ] **S15.T10** Monolith consumer updating the tenant replica; version check for out-of-order events
  Must know: idempotent consumer, versions

- [ ] **S15.T11** `provisioning` state page in the monolith; one-off migration of existing tenants and comparison
  Must know: eventual consistency UX

## Provisioning saga

- [ ] **S15.T12** Saga: admin creates tenant → event → monolith provisions → `tenant.provisioned`/`provisioning_failed` → activate + invite
  Must know: orchestration saga

- [ ] **S15.T13** Timeouts, retries, compensating steps; recovery after monolith downtime; ADR 0031 orchestration vs choreography
  Must know: saga failure handling

## Billing

- [ ] **S15.T14** `Subscription`, `Invoice`, `Payment` models, DRF API, admin
  Must know: DRF ViewSets, serializers

- [ ] **S15.T15** Tenant state machine `trial → active → past_due → suspended → cancelled` with events; monolith shows suspended page
  Must know: state machine in Django

- [ ] **S15.T16** Entitlements (limits, feature flags) sent by event; monolith checks locally; ADR 0032
  Must know: entitlements, feature flags

- [ ] **S15.T17** Payme/Click webhooks in DRF: signature, idempotency, tiyin amounts
  Must know: payment webhooks, HMAC

- [ ] **S15.T18** Celery beat: invoices, reminders, grace period, auto-suspension; payment reconciliation
  Must know: periodic tasks

## Service auth

- [ ] **S15.T19** Impersonation tokens (RS256, JWKS endpoint); monolith verifies, marks session, audits
  Must know: asymmetric JWT, JWKS

- [ ] **S15.T20** Service tokens for internal API; `[EXT]` mTLS
  Must know: service-to-service auth

- [ ] **S15.T21** DRF concepts applied: throttling, django-filter, drf-spectacular; ADR 0033 DRF vs FastAPI comparison
  Must know: DRF ecosystem

- [ ] **S15.T22** `[EXT]` Self-service signup endpoint with OTP, rate limiting, abuse protection
  Must know: public endpoints hardening
