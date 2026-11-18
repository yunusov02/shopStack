# Slice specs

Each phase file holds one phase. Every slice lists **Files**, **Models**, **Endpoints**, **Steps** and **Tests**. Treat later phases as a draft: revise each phase's spec when you reach it, using what earlier slices taught you.

## Conventions

```
src/retail/
  main.py              # create_app()
  core/                # settings, db, uow, errors, idempotency, logging
  modules/<name>/
    router.py  schemas.py  service.py  repository.py  models.py
migrations/versions/
tests/unit/  tests/integration/
services/<name>/       # from Phase G
```

- IDs are UUIDs. Money is `numeric(14,2)` in Postgres, `Decimal` in Python, a string in JSON. Quantities are `numeric(12,3)`.
- Every business table has `tenant_id uuid not null` and `created_at timestamptz not null default now()`.
- API prefix `/api/v1`. Error body: `{"error": {"code", "message", "details"}}`. `404` missing or another tenant's, `409` state conflict, `422` validation.
- One migration per slice: `NNNN_<slice-name>.py`.
- Tests for slice N live in `tests/integration/test_sNN_<name>.py`; test names in the specs are the function names to write.
- Routers stay thin: parse, call one service method, return. Services own transactions through the Unit of Work.

## Frontend

Every UI is a React + TypeScript app in one pnpm workspace. Backends serve JSON only; no server-rendered pages.

```
frontend/
  apps/back-office/      # slice 8
  apps/pos-terminal/     # PWA, slice 25
  apps/staff-admin/      # Platform and Audit staff UI, slice 30
  apps/storefront/       # web shop, slice 32
  apps/courier/          # PWA, slice 33
  apps/supplier-portal/  # slice 38
  packages/ui/           # shared components and design tokens
  packages/api-client/   # types generated from each backend's OpenAPI
```

- React 18, TypeScript `strict`, Vite, React Router, TanStack Query, react-hook-form + zod.
- `openapi-typescript` regenerates the API types in CI, so a backend change that breaks a frontend fails the build.
- i18n with uz-Latn, uz-Cyrl and ru from the first screen.
- Auth: the back-office, staff admin and supplier portal use an HttpOnly session cookie plus a CSRF header; the POS and courier apps use JWT.
- Tests: Vitest + Testing Library for components, Playwright for end-to-end flows.
