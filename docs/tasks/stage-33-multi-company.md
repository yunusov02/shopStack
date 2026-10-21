# Stage 33: Multi-company and intercompany

Where: `modules/accounting`, `modules/inventory`. Prerequisites: stages 26 and 30.

- [ ] **S33.T01** `Company` model inside tenant: legal details, base currency, chart of accounts, fiscal calendar; `company_id` on locations, documents, journal entries (migration with backfill)
  Must know: large migrations with backfill

- [ ] **S33.T02** Company-aware permissions and queries; 404 across companies; isolation tests
  Must know: second isolation axis

- [ ] **S33.T03** Intercompany transfer: sale + receipt at transfer price, mirrored entries, intercompany accounts, one transaction
  Must know: intercompany accounting

- [ ] **S33.T04** Consolidation reports with elimination of intercompany balances
  Must know: consolidation

- [ ] **S33.T05** Tests: matching entries both sides, elimination, per-company trial balance
  Must know: integration tests

- [ ] **S33.T06** `[EXT]` Franchise mode with royalty invoices; `[OPT]` per-company schema/database ADR 0059
  Must know: isolation strategies
