# Stage 39: MLOps: serving, registry, monitoring, retraining

Where: `services/ml-serving`, `ml/pipelines`, Airflow, Kubernetes. Prerequisites: stages 38 and 21.

## Registry and packaging `[CORE]`

- [ ] **S39.T01** ADR 0073: separate serving service vs in-monolith; REST now, gRPC later; inference never inside a document transaction
  Must know: serving architectures

- [ ] **S39.T02** MLflow model registry: signatures, stages `candidate → staging → production → archived`, promotion as a logged transition with a reason
  Must know: model registry, model signatures

- [ ] **S39.T03** Packaging: model + feature transform + signature as one artifact; serving image built in CI from a registry version and tagged by it
  Must know: model packaging, CI for models

- [ ] **S39.T04** Versioning rules: immutable versions; predictions and the stage 29 planning run record the version
  Must know: provenance

## Serving `[CORE]`

- [ ] **S39.T05** Service skeleton `services/ml-serving`: FastAPI, JWKS auth, service token for the core, models loaded from the registry at start and on signal, health endpoints, Dockerfile, CI
  Must know: service template, JWKS

- [ ] **S39.T06** Batch inference DAG: nightly scoring of variants (forecast) and customers (churn) → Gold + online store; publishes `forecast.published.v1` and `customer_segment.changed.v1`; idempotent per `run_id`
  Must know: batch scoring, idempotency

- [ ] **S39.T07** Online `POST /v1/predict/<model>` with Pydantic signature; features from the Redis online store; `run_in_executor` for the model call; Locust test with p99 < 50 ms
  Must know: latency budgets, event loop and CPU-bound work

- [ ] **S39.T08** Training-serving skew check: nightly sample scored via batch and online features; alert on difference
  Must know: skew detection

- [ ] **S39.T09** Core-side adapter: timeout, retry budget, circuit breaker; fallbacks (yesterday's forecast, unchanged churn band); test that nothing in the core waits on the service when it is down
  Must know: adapters, fallbacks

- [ ] **S39.T10** Throughput lab: request batching inside the service, workers vs threads for a CPU-bound model; numbers in README
  Must know: GIL, batching

## Deployment strategies `[CORE]`

- [ ] **S39.T11** ADR 0074 and shadow deployment: candidate scores alongside production, outputs logged and compared, comparison report
  Must know: shadow deployment

- [ ] **S39.T12** Canary by tenant (consistent hashing on `tenant_id`), business metric per group, promotion or rollback by registry stage with no rebuild
  Must know: canary, consistent hashing

- [ ] **S39.T13** Rollback drill: production model broken on purpose, alert, previous version serving within five minutes, postmortem
  Must know: rollback rehearsal

## Monitoring and retraining `[CORE]`

- [ ] **S39.T14** ADR 0075 and monitoring metrics to Prometheus: infrastructure (latency, errors, throughput, memory), data drift (PSI, KS per feature, missing rates, new categories), model quality with delayed labels
  Must know: PSI, KS, delayed labels

- [ ] **S39.T15** Concept drift vs data drift note with project examples; which one retraining fixes
  Must know: drift types

- [ ] **S39.T16** Retraining DAG: scheduled and drift-triggered; retrain → backtest vs baseline and vs production → register candidate → shadow → promote (human approval via stage 30 `[EXT]`)
  Must know: retraining pipelines

- [ ] **S39.T17** Prediction logging to the lake (features, output, version, request id, no PII), partitioned; used for retraining and incidents
  Must know: prediction logs

- [ ] **S39.T18** Model cards generated from the registry; one per production model
  Must know: model cards

- [ ] **S39.T19** Kubernetes deploy of the serving service (stage 21 chart), HPA on request rate; planted feature drift in one tenant reported the same day
  Must know: Helm, HPA

## Extensions

- [ ] **S39.T20** `[EXT]` ONNX export and ONNX Runtime inference with before/after latency; gRPC endpoint and comparison; Grafana per-model dashboard with drift runbook
  Must know: ONNX, gRPC

- [ ] **S39.T21** `[OPT]` Quantization/pruning on a small neural model; GPU node pool; BentoML or KServe ADR; Kubeflow Pipelines; self-hosted → SageMaker/Vertex mapping note
  Must know: model optimisation, serving frameworks
