# Stage 4: Procurement

Where: `modules/procurement`. Prerequisites: stage 3. Done when, after partial receipt, return and payment, stock, cost and debt are correct.

## Suppliers and purchase orders `[CORE]`

- [ ] **S4.T01** `Supplier` model + migration: `tenant_id`, name, contacts (JSONB), payment terms (days), `is_active`
  Must know: JSONB for semi-structured data

- [ ] **S4.T02** Supplier repository, service, endpoints (CRUD, `purchase.create`)
  Must know: CRUD pattern

- [ ] **S4.T03** `PurchaseOrder` + `PurchaseOrderLine` models + migration: status (`draft → pending_approval → approved → sent → partially_received → received → closed / cancelled`), supplier, location, expected date, line qty/price/received qty, totals in `Numeric`
  Must know: document + lines, Decimal totals

- [ ] **S4.T04** PO `transition()` with allowed transitions table and a transition log
  Must know: state machine pattern (reuse S3.T20 approach)

- [ ] **S4.T05** `PurchaseOrderService`: create draft, submit, approve by amount threshold (`purchase.approve`), send, cancel; audit on approve/cancel
  Must know: approval rules, audit

- [ ] **S4.T06** PO endpoints: CRUD draft, submit, approve, send, cancel, list with filters
  Must know: FastAPI, permissions

- [ ] **S4.T07** Tests: state machine, approval threshold, totals
  Must know: integration tests

- [ ] **S4.T08** `[EXT]` `PurchaseRequest` model + service: from a location, or auto-generated from reorder levels; converts to a PO
  Must know: document conversion

## Goods receipt and costing `[CORE]`

- [ ] **S4.T09** `GoodsReceipt` + lines models + migration: PO link, received qty per line, batch/expiry, discrepancy fields (short, excess, damaged)
  Must know: partial receipt modelling

- [ ] **S4.T10** `GoodsReceiptService.receive(po, lines)`: `receive` movements via `StockService`, update PO received quantities and status (`partially_received`/`received`), batches created
  Must know: cross-module service calls inside one UoW

- [ ] **S4.T11** ADR 0012: costing method (WAC vs FIFO)
  Must know: weighted average cost, FIFO layers

- [ ] **S4.T12** `VariantCost` model + migration (per tenant+location or per tenant, per ADR): `avg_cost Numeric(14,4)`, `on_hand_for_cost`
  Must know: cost precision

- [ ] **S4.T13** WAC recalculation on receipt inside the receipt transaction, with `with_for_update` on the cost row; parallel receipts test
  Must know: row locks, Decimal rounding, concurrency tests

- [ ] **S4.T14** Receipt endpoints: create receipt for PO, view receipts
  Must know: FastAPI

- [ ] **S4.T15** `SupplierReturn` model + service: return to supplier creates negative `receive` (or `return_to_supplier`) movements and a credit against payables
  Must know: reversal documents

- [ ] **S4.T16** Tests: partial receipt flow, WAC values, supplier return
  Must know: Decimal assertions

## Payables `[CORE]`

- [ ] **S4.T17** `PayableInvoice` model + migration: supplier, receipt link, amount, due date, status
  Must know: invoice lifecycle

- [ ] **S4.T18** `PayableLedgerEntry` model + migration (append-only): invoice, payment, credit; supplier balance = sum of entries
  Must know: ledger pattern

- [ ] **S4.T19** `PayablesService`: invoice from receipt, record payment (partial), credit from return; balance query; `finance.view`
  Must know: ledger sums, partial payments

- [ ] **S4.T20** Payables endpoints: invoices, payments, supplier balance and statement
  Must know: reporting endpoints

- [ ] **S4.T21** Purchase history endpoint: POs, receipts, returns per supplier/variant with cursor pagination
  Must know: keyset pagination

- [ ] **S4.T22** Tests: debt after receipt, payment, return; statement equals ledger sum
  Must know: integration tests

- [ ] **S4.T23** `[EXT]` Supplier performance report: average lead time, share of discrepancies
  Must know: aggregate SQL, date math

- [ ] **S4.T24** `[OPT]` Landed cost: allocate transport cost across receipt lines (by value or quantity) into WAC
  Must know: allocation with largest remainder
