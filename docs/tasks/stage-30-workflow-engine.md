# Stage 30: Workflow, approvals and document engine

Where: `modules/workflow`. Prerequisites: stages 5 and 11.

- [ ] **S30.T01** Generic state machine framework: declarative states/transitions/guards/effects; `transition()` with log; test forbidding direct status writes
  Must know: generic frameworks, Python descriptors/registries

- [ ] **S30.T02** Characterisation tests for every existing state machine before migration
  Must know: characterisation tests

- [ ] **S30.T03** Migrate sale, PO, transfer, order, contract, work order to the framework (one PR each)
  Must know: refactoring under test

- [ ] **S30.T04** `ApprovalWorkflow` + `ApprovalStep` + `ApprovalInstance` models: role/user approvers, thresholds, parallel/sequential, delegation, timeout escalation
  Must know: workflow modelling

- [ ] **S30.T05** Approval engine service; step-up PIN as a step type; migrate existing approvals
  Must know: engine design

- [ ] **S30.T06** `DocumentSequence` model: per type/location, prefix, yearly reset, gapless flag; ADR 0056
  Must know: sequences, gapless cost

- [ ] **S30.T07** Inbox endpoint ("waiting for me") + notifications
  Must know: queries across document types

- [ ] **S30.T08** Workflow versioning: in-flight documents pinned to their version; configuration is audited
  Must know: versioned config

- [ ] **S30.T09** Tests: tenant adds an approval step without deploy; all old tests green
  Must know: regression suites

- [ ] **S30.T10** `[EXT]` SLA timers and lead-time report; `[OPT]` HTMX workflow editor
  Must know: timers
