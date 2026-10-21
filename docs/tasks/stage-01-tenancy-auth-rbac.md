# Stage 1: Tenancy, auth and RBAC

Prerequisites: stage 0. Done when tenant isolation, RLS, OTP and RBAC tests are green.

## Tenancy `[CORE]`

- [ ] **S1.T01** `Tenant` model + migration: `id`, `name`, `slug`, `status` (`active | suspended | provisioning`), timestamps
  Must know: SQLAlchemy models, enums in Postgres, Alembic

- [ ] **S1.T02** `Domain` model + migration: `tenant_id`, `host` (unique), `is_primary`; subdomain validation (RFC 1123 labels, reserved names)
  Must know: FK, unique constraint, regex validation, DNS labels

- [ ] **S1.T03** `Location` model + migration: `tenant_id`, `name`, `type` (`store | warehouse`), `is_active`
  Must know: enum columns, check constraints

- [ ] **S1.T04** `TenantSettings` model + migration: currency, time zone (IANA), tax regime, receipt format; one row per tenant
  Must know: one-to-one relationship, `zoneinfo`

- [ ] **S1.T05** Tenant context with `contextvars`: `get_current_tenant_id()`, set/reset helpers; fails closed (raises if unset)
  Must know: `contextvars`, ASGI concurrency, fail-closed design

- [ ] **S1.T06** Tenant-resolving middleware: `Host` header → `Domain` → tenant id into the context var; unknown host → 404
  Must know: ASGI middleware, `Host` header, 404 vs 403

- [ ] **S1.T07** Redis client in lifespan; cache `host → tenant_id` with TTL and invalidation on domain change
  Must know: redis-py async, TTL, cache invalidation

- [ ] **S1.T08** `TenantMixin` (`tenant_id` column, FK, index) and a SQLAlchemy global filter: every query on a tenant model gets `WHERE tenant_id = :current`; no context → error
  Must know: `do_orm_execute` event, `with_loader_criteria`, mixins

- [ ] **S1.T09** Repositories set `tenant_id` on `add` from the context; a test that an insert without context fails
  Must know: SQLAlchemy events or repository base class

- [ ] **S1.T10** DB roles: `app` role (RLS-limited) and `app_admin` role (bypass); migration creates roles and grants
  Must know: Postgres roles, `GRANT`, `RunSQL`-style raw migrations in Alembic

- [ ] **S1.T11** RLS policies on every tenant table: `ENABLE` + `FORCE ROW LEVEL SECURITY`, policy on `current_setting('app.tenant_id')`
  Must know: RLS, `current_setting`, `SET LOCAL`

- [ ] **S1.T12** Set `app.tenant_id` with `SET LOCAL` at the start of every UoW transaction
  Must know: `SET LOCAL`, transaction scope, UoW hook

- [ ] **S1.T13** RLS coverage test: iterate every tenant-owned table and assert RLS is enabled and forced
  Must know: `pg_class.relrowsecurity`, `information_schema`

- [ ] **S1.T14** Isolation tests: two tenants, every tenant table, reads and writes cross-tenant → empty/404; global filter and RLS tested separately
  Must know: parametrized tests, fixtures for two tenants

## Auth `[CORE]`

- [ ] **S1.T15** `User` model + migration: global (no tenant), phone E.164 unique, password hash, `is_active`, timestamps
  Must know: E.164 format, phonenumbers library (ADR if added), unique index

- [ ] **S1.T16** `Membership` model + migration: `user_id`, `tenant_id`, `status`, unique `(user_id, tenant_id)`
  Must know: composite unique constraint, many-to-many through a model

- [ ] **S1.T17** Password hashing with Argon2 (`argon2-cffi`): `hash`, `verify`, `needs_rehash`
  Must know: Argon2id parameters, salting, why not bcrypt/sha256

- [ ] **S1.T18** `UserRepository` and `MembershipRepository`: `get_by_phone`, `get_memberships(user_id)`, `add`
  Must know: repository pattern, `selectinload`

- [ ] **S1.T19** `AuthService.register(phone, password)` and `login(phone, password)`: duplicate phone and wrong password → domain errors; constant-time behaviour on unknown phone
  Must know: service layer, custom exceptions, timing attacks

- [ ] **S1.T20** API standards: error format from S0.T16 reused, `/api/v1/` prefix, OpenAPI tags and examples
  Must know: FastAPI routers, OpenAPI, `responses=` docs

- [ ] **S1.T21** JWT access tokens (short TTL, `sub`, `tenant_id`, `membership_id`, `jti`) with `PyJWT` (ADR); `get_current_user` dependency checking the tenant claim against the context
  Must know: JWT structure, claims, HS256 vs RS256, `exp`/`iat`

- [ ] **S1.T22** Refresh tokens: stored hashed in DB with family id; rotation on use; reuse detection revokes the family
  Must know: refresh token rotation, token families, reuse detection

- [ ] **S1.T23** Endpoints: `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`, `GET /users/me`
  Must know: FastAPI router, Pydantic v2 schemas, status codes

- [ ] **S1.T24** Server-side session for the back-office: session id cookie (`HttpOnly`, `Secure`, `SameSite`), data in Redis with TTL, sliding expiry
  Must know: cookies, session storage, Redis hashes

- [ ] **S1.T25** CSRF protection for cookie sessions: double-submit token, checked on unsafe methods; HTMX header support
  Must know: CSRF, double-submit cookie, `SameSite`

- [ ] **S1.T26** ADR 0006: access vs refresh tokens, JWT for POS vs Redis session for back-office, stateless API
  Must know: sessions vs tokens trade-offs

- [ ] **S1.T27** Web security baseline: parametrised queries only (a test with a hostile input), Jinja2 autoescape on, `Content-Security-Policy` and other security headers middleware, outbound URL validator (blocks private IPs) for later webhooks
  Must know: SQL injection, XSS, CSP, SSRF, security headers

- [ ] **S1.T28** Auth tests: register/login/refresh/rotation/reuse detection, session + CSRF, security headers
  Must know: httpx cookies, time freezing

## OTP and 2FA `[CORE]`

- [ ] **S1.T29** `OtpCode` model + migration: phone, code hash, purpose, `expires_at`, attempts, `created_at`
  Must know: hashing short codes, TTL columns

- [ ] **S1.T30** `OtpService.send(phone, purpose)`: generate, hash, store, cooldown per phone (Redis), `SmsProvider` port with a fake implementation
  Must know: `secrets`, cooldown, ports and adapters

- [ ] **S1.T31** `OtpService.verify(phone, code)`: atomic attempt increment (`UPDATE ... RETURNING`), max attempts, expiry, single use; same response for unknown phone (enumeration protection)
  Must know: atomic UPDATE, enumeration attacks

- [ ] **S1.T32** Endpoints: `POST /auth/otp/send`, `POST /auth/otp/verify`
  Must know: FastAPI, rate-limit interplay

- [ ] **S1.T33** TOTP 2FA: secret per user (encrypted at rest), enrol with QR (otpauth URL), verify on login for owners and managers, recovery codes (hashed)
  Must know: TOTP (RFC 6238), `pyotp` (ADR), encryption at rest

- [ ] **S1.T34** Rate limiting middleware: sliding window in Redis per IP and per phone on auth endpoints; `429` with `Retry-After`
  Must know: sliding window algorithm, Redis sorted sets or Lua, 429 semantics

- [ ] **S1.T35** OTP, TOTP and rate limit tests (cooldown, attempts, expiry, enumeration, 429)
  Must know: fake time, fake SMS provider

## RBAC `[CORE]`

- [ ] **S1.T36** Permission codes as an `enum`/`Literal` in code (the roadmap list); a test that every code is unique and documented
  Must know: enums, single source of truth in code

- [ ] **S1.T37** `Role` model + migration: `tenant_id`, `name`, `permissions` (array or JSONB), `is_system`; `MembershipRole` link
  Must know: array/JSONB columns, link tables

- [ ] **S1.T38** `MembershipLocation` model + migration: allowed locations per membership
  Must know: many-to-many, composite PK

- [ ] **S1.T39** Default role seeding on tenant creation: Owner, Admin, Branch Manager, Cashier, Warehouse Manager, Accountant, Sales Manager with permission sets
  Must know: seed data, idempotent inserts

- [ ] **S1.T40** `require_permission("sale.create")` dependency: loads membership, roles, checks the code; `403` without it
  Must know: FastAPI dependency with parameters, caching per request

- [ ] **S1.T41** Object-level location check helper: object in another tenant or an unallowed location → `404`
  Must know: 404 vs 403 reasoning, fail closed

- [ ] **S1.T42** Role management endpoints: list, create, update roles; assign roles and locations to memberships (`staff.manage`)
  Must know: CRUD endpoints, permission dependency

- [ ] **S1.T43** Role × permission × endpoint matrix test: a table of (role, endpoint) → expected status, run with parametrize
  Must know: pytest parametrize, test matrices

- [ ] **S1.T44** `[EXT]` Custom tenant roles with privilege escalation protection: can only grant permissions you hold; test
  Must know: privilege escalation, set operations

- [ ] **S1.T45** `[EXT]` ADR 0007: RBAC vs ABAC and where location access is an attribute check
  Must know: RBAC, ABAC

- [ ] **S1.T46** `[OPT]` OAuth 2.0 / OIDC login with an external provider behind the auth service; ADR
  Must know: OAuth 2.0 authorization code flow, OIDC, PKCE

## Platform operations (temporary) `[CORE]`

- [ ] **S1.T47** `create_tenant` command as an idempotent service function: tenant, primary domain, default location, roles, owner user and membership in one transaction; idempotency by slug
  Must know: idempotent commands, one transaction for many inserts

- [ ] **S1.T48** CLI (`typer` or `python -m`) wrapper and an internal-only endpoint (bound to a separate internal router/port) for tenant creation
  Must know: CLI entrypoints, internal network exposure

- [ ] **S1.T49** Internal operations run under the `app_admin` role in a separate process/engine (bypasses RLS)
  Must know: separate engine per role, RLS bypass

- [ ] **S1.T50** `Invite` model + migration + service: token hash, expiry, accept creates membership; sending stubbed via the SMS port
  Must know: one-time tokens, expiry

- [ ] **S1.T51** `AuditLog` model + migration: append-only (no UPDATE/DELETE grants + trigger), `actor`, `action`, `object_type`, `object_id`, `before`, `after`, `reason`, `correlation_id`; `audit()` helper used by sensitive operations
  Must know: append-only tables, triggers, JSONB

- [ ] **S1.T52** Tests: tenant creation idempotency, invites, audit append-only enforcement
  Must know: raw SQL in tests, expecting DB errors
