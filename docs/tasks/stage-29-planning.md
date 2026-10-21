# Stage 29: Demand planning and replenishment

Where: `modules/planning`. Prerequisites: stages 4 and 16.

- [ ] **S29.T01** ADR 0055: where the forecast runs (Analytics) and how results return to the core
  Must know: service boundaries

- [ ] **S29.T02** Forecast job: moving average, exponential smoothing, weekday profile; `DemandForecast` table
  Must know: forecasting basics

- [ ] **S29.T03** `ReplenishmentParams` model: lead time, safety stock, review period, MOQ, pack size, max
  Must know: inventory parameters

- [ ] **S29.T04** Projected stock and reorder point computation (pure function) with unit tests
  Must know: reorder point formula

- [ ] **S29.T05** Planning run (beat + distributed lock) producing a `PlanningRun` snapshot with suggestions
  Must know: snapshot runs, locks

- [ ] **S29.T06** Suggested POs grouped by supplier (MOQ, pack size) → draft POs; `replenishment.suggested.v1`
  Must know: grouping, document creation

- [ ] **S29.T07** Transfer suggestions between locations before buying
  Must know: multi-location logic

- [ ] **S29.T08** Exception report: stock-outs, overstock, dead stock, MAPE
  Must know: forecast error metrics

- [ ] **S29.T09** Endpoints and tests on seeded history
  Must know: integration tests

- [ ] **S29.T10** `[EXT]` Promotion-aware forecast, open-to-buy; `[OPT]` supplier forecast sharing
  Must know: demand lifts
