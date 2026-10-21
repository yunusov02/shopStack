# Stage 19: Integrations

Where: `modules/integrations`. Prerequisites: stage 18 (parts earlier).

- [ ] **S19.T01** Interfaces: `PaymentProvider`, `FiscalProvider`, `SmsProvider`, `ReceiptPrinter`; fakes with failure modes
  Must know: ports and adapters, Protocol

- [ ] **S19.T02** Resilience wrapper: timeouts, retries with backoff + jitter, circuit breaker (states, half-open), bulkhead (pool per provider)
  Must know: circuit breaker, bulkhead

- [ ] **S19.T03** Graceful degradation at POS: card unavailable → cash still works; UI message
  Must know: fallback design

- [ ] **S19.T04** `WebhookEndpoint` + `WebhookDelivery` models: tenant endpoints, HMAC signatures, retries, delivery log; SSRF-safe URL validation
  Must know: outbound webhooks, HMAC, SSRF

- [ ] **S19.T05** Webhook dispatcher task and management endpoints
  Must know: Celery tasks

- [ ] **S19.T06** Tests: breaker opens on timeouts, POS keeps selling, webhook retries logged
  Must know: fault injection

- [ ] **S19.T07** `[EXT]` Card/QR payment provider adapters at POS
  Must know: provider APIs

- [ ] **S19.T08** `[EXT]` Fiscal adapter + mock per current Uzbek requirements
  Must know: fiscalization rules

- [ ] **S19.T09** `[EXT]` ESC/POS printer, scanner keyboard mode, scale integration
  Must know: ESC/POS

- [ ] **S19.T10** `[EXT]` 1C export formats
  Must know: file exchange formats
