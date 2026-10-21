# Stage 20: Observability

Prerequisites: stage 19.

- [ ] **S20.T01** Correlation ID across HTTP, Kafka, RabbitMQ, Celery in every service
  Must know: context propagation

- [ ] **S20.T02** OpenTelemetry: auto-instrument FastAPI, Django, SQLAlchemy, httpx, Celery, Kafka; OTLP collector in Compose; one trace per sale across services
  Must know: OpenTelemetry SDK, spans

- [ ] **S20.T03** Prometheus: RED metrics per service, business metrics, outbox backlog, consumer lag, queue length, DLQ size, sync delay
  Must know: Prometheus client, metric types

- [ ] **S20.T04** Structured logging contract (JSON, correlation id, tenant, no PII); Loki + Promtail in Compose
  Must know: structlog, Loki

- [ ] **S20.T05** Grafana dashboards (overview + per service), alert rules with runbooks, Sentry
  Must know: Grafana, alerting

- [ ] **S20.T06** SLIs/SLOs document: p50/p95/p99, success rate, error budget policy
  Must know: SLO engineering

- [ ] **S20.T07** Liveness/readiness in every service; synthetic checks for login, sale, checkout
  Must know: probes, synthetic monitoring

- [ ] **S20.T08** Chaos experiments (kill consumer, stop Redis, slow provider) with postmortems
  Must know: chaos engineering, postmortem template
