# Stage 14: Notification service

Where: `services/notification`. Prerequisites: stage 13.

- [ ] **S14.T01** Service skeleton: worker (RabbitMQ consumer) + FastAPI health/status app, own Postgres, Dockerfile, CI
  Must know: service template, Compose

- [ ] **S14.T02** `notification.send.v1` command schema (`message_id`, tenant, recipient, channel, template, variables, locale, priority)
  Must know: command vs event

- [ ] **S14.T03** `Template` model + migration: platform defaults, tenant overrides, locales, versions; rendering with variable validation
  Must know: Jinja2 sandbox, versioned templates

- [ ] **S14.T04** `Message` model + migration with state machine `queued → sending → sent → delivered / failed`, attempts log, rendered text snapshot
  Must know: state machine

- [ ] **S14.T05** Provider adapters: `SmsProvider`, `TelegramProvider`, `EmailProvider` interfaces + fakes
  Must know: ports and adapters

- [ ] **S14.T06** Idempotent consumer (`message_id` unique), ack after attempt recorded
  Must know: at-least-once, manual ack

- [ ] **S14.T07** Delay queues (TTL + DLX) for exponential backoff; DLQ after max attempts; replay CLI
  Must know: RabbitMQ DLX, TTL queues

- [ ] **S14.T08** Priority queues; per-provider rate limit (token bucket) and circuit breaker
  Must know: priority, token bucket, circuit breaker

- [ ] **S14.T09** Provider delivery callbacks endpoint → status updates
  Must know: webhooks inbound

- [ ] **S14.T10** Core: send electronic receipts, OTP and invites through the service; remove old sending code
  Must know: refactor to commands

- [ ] **S14.T11** Recipient preferences (channel, marketing opt-out); privacy: masked logs, body retention job
  Must know: PII handling

- [ ] **S14.T12** Chaos test: provider down 10 minutes → no loss, no duplicates, DLQ replay works
  Must know: fault injection in tests

- [ ] **S14.T13** `[EXT]` Fallback channel, quiet hours, cost tracking per tenant, owner Telegram bot daily report
  Must know: fallback logic, scheduling
