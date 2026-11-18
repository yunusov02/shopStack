# Phase C specs: production

### 12 · The app runs on a VPS

**Files:** `Dockerfile`, `.dockerignore`, `deploy/docker-compose.prod.yml`, `deploy/Caddyfile`, `deploy/deploy.sh`, `deploy/backup.sh`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml`, `core/health.py`, `tests/README.md`

**Endpoints**

- `GET /health/live` (process is up)
- `GET /health/ready` (Postgres and Redis reachable)

**Steps**

1. Multi-stage Dockerfile: builder runs `uv build`; runtime is `python:3.12-slim`, non-root user, installs the wheel.
2. Production Compose: app, Postgres with a volume, Redis, Caddy with automatic TLS; secrets in an env file outside git.
3. A `migrate` service runs `alembic upgrade head`; the app waits for it with `service_completed_successfully`.
4. `deploy.sh`: pull the image for `IMAGE_TAG=<sha>`, `up -d`, poll `/health/ready`, roll back to the previous tag on failure.
5. `backup.sh`: nightly `pg_dump` copied off the server; one rehearsed restore into a fresh container followed by `reconcile_stock.py`.
6. After the first broken deploy (write it up in an ADR), CI: `ruff check`, `ruff format --check`, `mypy`, `pytest` with Testcontainers, `alembic check`, upgrade and downgrade on an empty DB, build and push the image tagged with the commit SHA.
7. pre-commit: ruff, mypy, trailing whitespace.

**Tests**

- `test_ready_returns_503_when_db_down`
- CI fails on a model change without a migration
- A deliberately broken image rolls back automatically
- A restored backup passes the stock reconciliation

### 13 · The app is safe on the internet

**Files:** `core/security/{rate_limit,headers,csrf}.py`, `modules/accounts/{otp,totp}.py`, `migrations/versions/0013_otp_totp.py`

**Models**

- `otp_codes`: `id`, `phone`, `purpose`, `code_hash`, `expires_at`, `attempts`, `consumed_at`
- `users`: add `totp_secret_encrypted`, `totp_enabled_at`; `recovery_codes`: `user_id`, `code_hash`, `used_at`

**Endpoints**

- `POST /api/v1/auth/otp/request` `{phone}`; `POST /api/v1/auth/otp/verify` `{phone, code}`
- `POST /api/v1/me/totp/setup` → `otpauth://` URI; `POST /api/v1/me/totp/confirm` `{code}`
- `POST /api/v1/auth/totp` `{code}` (second login step)

**Steps**

1. Sliding-window limiter in Redis (sorted set or a Lua script), per IP and per phone; `429` with `Retry-After`.
2. CSRF token (double-submit cookie) checked on every unsafe request from the React apps, which send it in a header.
3. Headers middleware: HSTS, `X-Content-Type-Options`, `Referrer-Policy`, CSP with no inline scripts and `frame-ancestors 'none'`.
4. CORS allowlist with the POS origin only.
5. OTP: 6 digits, stored hashed, 5-minute TTL, 5 attempts, 60-second cooldown, consumed atomically; identical response for unknown phones. Sent through a fake SMS adapter that logs, until slice 28.
6. TOTP required for owner and manager roles; secret encrypted at rest; recovery codes.
7. Review DB role privileges; JWT scopes `pos` and `admin`.

**Tests**

- `test_login_rate_limited_after_n_attempts`
- `test_otp_cannot_be_reused` and `test_otp_attempt_limit`
- `test_otp_request_same_response_for_unknown_phone`
- `test_form_without_csrf_token_rejected`
- `test_security_headers_present`
- `test_sql_injection_payloads_return_no_extra_rows`
- `test_owner_login_requires_totp`

### 14 · A production bug can be traced

**Files:** `core/logging.py`, `core/correlation.py`, `core/sentry.py`, `docs/runbooks/find-request-logs.md`

**Steps**

1. structlog JSON output; processors add timestamp, level, `request_id`, `tenant_id`, `user_id` from context variables.
2. Correlation ID: accept a valid `X-Request-ID`, otherwise generate one; return it in the response and on the error page.
3. Redaction processor for phone, password and token fields.
4. Sentry with the FastAPI integration, `release = GIT_SHA`, `environment`, `before_send` scrubbing.
5. One access log line per request with duration and status.
6. Runbook: from a user's screenshot of the request ID to every log line of that request.

**Tests**

- `test_response_has_request_id_header`
- `test_log_lines_include_tenant_and_request_id`
- `test_phone_and_password_are_redacted`
- `test_unhandled_error_is_reported_to_sentry` (fake transport)
