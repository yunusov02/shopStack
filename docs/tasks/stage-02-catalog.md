# Stage 2: Catalog

Where: `modules/catalog`. Prerequisites: stage 1. Done when a cashier finds a product by barcode, scale barcode, SKU or name, and location and wholesale prices resolve correctly.

## Product model `[CORE]`

- [ ] **S2.T01** ADR 0008: category tree storage (adjacency list vs materialized path vs `ltree`)
  Must know: tree storage patterns, `ltree`, recursive CTE

- [ ] **S2.T02** `Category` model + migration (per the ADR), `Brand` model + migration; unique name per tenant
  Must know: self-referencing FK, unique per tenant

- [ ] **S2.T03** ADR 0009: variant attributes (EAV vs JSONB vs separate tables)
  Must know: EAV, JSONB, GIN index on JSONB

- [ ] **S2.T04** `Product` model + migration: `tenant_id`, name, category, brand, `tracking` (`none | serial | batch`), `is_archived`, `archived_at`
  Must know: enums, soft delete columns

- [ ] **S2.T05** `ProductVariant` model + migration: `product_id`, `sku` (unique per tenant), attributes (per ADR), `unit_id`, `is_weighted`, `tax_rate`
  Must know: unique composite index, Decimal column for tax rate

- [ ] **S2.T06** `Unit` model + migration: name, code, `is_weight`; quantities everywhere `Numeric(12, 3)`
  Must know: `Numeric` precision/scale, Decimal in Python

- [ ] **S2.T07** `Barcode` model + migration: `variant_id`, `value`, `type` (`ean13 | upc | qr | internal`), unique `(tenant_id, value)`
  Must know: barcode types, unique constraints

- [ ] **S2.T08** EAN-13 / UPC check digit validator (pure function) + unit tests
  Must know: check digit algorithm, pure functions

- [ ] **S2.T09** Scale barcode parser: prefixed EAN-13 → (item code, weight or price); tenant-configurable prefix and format; unit tests
  Must know: weight-embedded barcodes (prefix 2x), Decimal arithmetic

- [ ] **S2.T10** `CatalogRepository`: product/variant/barcode lookups, archive, list with filters
  Must know: joins, `selectinload`, filtering

- [ ] **S2.T11** `CatalogService`: create/update product and variants, add barcode (duplicate → domain error), archive (never hard delete; sold products cannot be deleted)
  Must know: service layer, domain errors, soft delete rules

- [ ] **S2.T12** Schemas and endpoints: categories, brands, units, products, variants, barcodes (`product.read`, `product.update`)
  Must know: FastAPI CRUD, Pydantic nested models, permission dependency

- [ ] **S2.T13** Tests: model constraints, service rules, endpoints, cross-tenant 404
  Must know: integration tests, parametrize

## Product model `[EXT]`

- [ ] **S2.T14** `Bundle`: model + migration (`bundle_variant_id`, components with quantities); sale will deduct components (hook for stage 5)
  Must know: composition models

- [ ] **S2.T15** `Kit`: model + migration; `assemble(kit, qty)` service that records component decrements and kit increment (stock calls land in stage 3); ADR 0010: bundle vs kit
  Must know: assembly vs bundle, cross-module calls

- [ ] **S2.T16** Serial-tracked variants: `SerialNumber` model + migration (`status: in_stock | sold | returned`), uniqueness per tenant
  Must know: serial tracking, state columns

- [ ] **S2.T17** Batches: `Batch` model + migration (`variant_id`, `batch_no`, `expires_at`), used by stage 3 movements
  Must know: lot tracking, expiry dates

## Prices `[CORE]`

- [ ] **S2.T18** `PriceList` model + migration: `tenant_id`, name, `type` (`retail | wholesale`), `currency`, `location_id` nullable, `is_default`
  Must know: nullable FK, one default per tenant (partial unique index)

- [ ] **S2.T19** `PriceListItem` model + migration: `price_list_id`, `variant_id`, `price Numeric(14,2)`, `valid_from`, `valid_to`; unique per list+variant+period
  Must know: Decimal money, validity ranges, exclusion constraints `[OPT]`

- [ ] **S2.T20** `PriceHistory` model + migration: append-only record on every price change (old, new, actor, reason)
  Must know: append-only history

- [ ] **S2.T21** `PricingRepository` and `PriceService.set_price(...)`: requires `product.update_price`, writes history and audit log in the same transaction
  Must know: sensitive operations, audit helper from S1.T51

- [ ] **S2.T22** `resolve_price(variant, location, price_list_type)`: location list → wholesale → default retail (basic order, extended in stage 6)
  Must know: resolution order, pure function

- [ ] **S2.T23** Price endpoints: price lists CRUD, set price, price history, resolved price
  Must know: FastAPI, Decimal serialization in Pydantic

- [ ] **S2.T24** Tests: permission on price change, history and audit written, resolution order
  Must know: integration tests

## Search `[CORE]`

- [ ] **S2.T25** Migration: `pg_trgm` extension, GIN trigram index on product and variant names, B-tree indexes on `sku` and `barcode.value`
  Must know: `pg_trgm`, GIN vs B-tree, `CREATE EXTENSION`

- [ ] **S2.T26** `search(query)` service: barcode exact → SKU exact → name trigram similarity; returns the match type
  Must know: `similarity()`, `ILIKE` vs trigram, ordering by rank

- [ ] **S2.T27** QR scan handling: extract a product identifier from a plain code or a URL, route to barcode search
  Must know: URL parsing, QR payload formats

- [ ] **S2.T28** `GET /catalog/search?q=` endpoint, limited results, cursor pagination not needed yet
  Must know: query params, response models

- [ ] **S2.T29** Performance test: seed 100k variants, assert barcode and SKU lookups under 10 ms using `EXPLAIN ANALYZE`; results in README
  Must know: `EXPLAIN (ANALYZE, BUFFERS)`, index scan vs seq scan, seeding scripts
