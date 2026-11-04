# Stage 11: HR (minimal)

Where: `modules/hr`. Prerequisites: stage 10. Done when the main flow works.

- [ ] **S11.T01** `Employee` model + migration: user, membership, position, location, hired_at
  Must know: links to auth models

- [ ] **S11.T02** `Candidate` model + migration with state machine `candidate → interview → offer → hired / rejected`; transition log
  Must know: state machine pattern

- [ ] **S11.T03** `HiringService.hire()`: creates Membership and role in the same transaction (cross-module side effect through the accounts service, not direct table writes)
  Must know: cross-module service calls

- [ ] **S11.T04** Endpoints: employees CRUD, candidate transitions (`staff.manage`)
  Must know: FastAPI

- [ ] **S11.T05** Tests: hire flow creates membership; invalid transitions rejected
  Must know: integration tests

- [ ] **S11.T06** `[EXT]` `Schedule` and `Attendance` models + endpoints
  Must know: time ranges, time zones

- [ ] **S11.T07** `[EXT]` Cashier KPI report (sales, average receipt, refunds per cashier)
  Must know: aggregate queries
