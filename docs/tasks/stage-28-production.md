# Stage 28: Production

Where: `modules/production`. Prerequisites: stages 4 and 26.

- [ ] **S28.T01** `BillOfMaterials` + `BomLine` models + migration: versioned, multi-level, scrap %, by-products; cycle detection
  Must know: graph cycles (DFS), versioning

- [ ] **S28.T02** `WorkOrder` model + state machine `draft → planned → released → in_progress → completed / cancelled`; partial completion
  Must know: state machines

- [ ] **S28.T03** Consumption: reservation on release; `production_consume` movements; ADR 0053 backflush vs manual; FEFO batches
  Must know: stock movements, FEFO

- [ ] **S28.T04** Output: `production_output` movement with new batch; by-products; scrap movements with reasons
  Must know: movement types

- [ ] **S28.T05** WIP accounting: consumption → WIP, completion → inventory; labour/overhead rate (ADR 0054); cost variance report
  Must know: WIP, standard vs actual cost

- [ ] **S28.T06** Availability check ("can I make N?") and shortage report
  Must know: BOM explosion

- [ ] **S28.T07** Endpoints and tests: multi-level BOM end to end; reconciliation still passes
  Must know: integration tests

- [ ] **S28.T08** `[EXT]` Routing/operations, capacity view, disassembly; `[OPT]` planning from forecast
  Must know: capacity planning basics
