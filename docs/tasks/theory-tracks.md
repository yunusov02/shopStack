# Theory tracks

One task per topic. Done when you can explain the topic with an example from this project (write 5–10 lines in `docs/notes/<track>.md`).

## Python internals (stages 1–9, Fluent Python)

- [ ] **TH.PY01** Decorators and closures → explain `Depends`, `@router.get`, `@task`
- [ ] **TH.PY02** Context managers and `contextvars` → UoW, tenant context
- [ ] **TH.PY03** Iterables, iterators, generators, comprehensions → streaming export
- [ ] **TH.PY04** Mutable default args, duck typing, EAFP vs LBYL, MRO, dunder methods
- [ ] **TH.PY05** Dataclass vs Pydantic vs SQLAlchemy model: which where
- [ ] **TH.PY06** Descriptors → how SQLAlchemy columns and Pydantic fields work
- [ ] **TH.PY07** Metaclasses and `__init_subclass__` → declarative models
- [ ] **TH.PY08** GIL, threads vs processes vs asyncio, I/O- vs CPU-bound, `run_in_executor`
- [ ] **TH.PY09** asyncio: event loop, tasks, cancellation, blocking calls
- [ ] **TH.PY10** Memory: refcount, cyclic GC, circular refs, `tracemalloc`
- [ ] **TH.PY11** Typing: generics, Protocol, TypedDict, mypy vs pyright; monkey patching
- [ ] **TH.PY12** Packaging: venv, uv vs poetry/pipenv, lock files, wheel vs sdist

## PostgreSQL internals (stages 3–10)

- [ ] **TH.PG01** MVCC: row versions, snapshots
- [ ] **TH.PG02** Isolation levels, SSI, anomalies per level
- [ ] **TH.PG03** Locks: row, table, advisory; `pg_locks`, deadlock detection
- [ ] **TH.PG04** Planner: statistics, join strategies, ignored indexes
- [ ] **TH.PG05** Normal forms and deliberate denormalization
- [ ] **TH.PG06** VACUUM, autovacuum, bloat
- [ ] **TH.PG07** WAL and checkpoints
- [ ] **TH.PG08** Replication: streaming, logical, lag, failover

## System design at scale (from stage 10, DDIA)

- [ ] **TH.SD01** B-tree vs LSM-tree
- [ ] **TH.SD02** Consistency models: strong, eventual, read-your-writes; ACID vs BASE
- [ ] **TH.SD03** Sharding, consistent hashing, hotspots
- [ ] **TH.SD04** CAP, partition tolerance, PACELC
- [ ] **TH.SD05** Consensus and leader election (Raft, KRaft, leases)
- [ ] **TH.SD06** HA: SPOF, failover, load balancers, stateless vs stateful
- [ ] **TH.SD07** Backpressure, thundering herd, bulkhead, graceful degradation
- [ ] **TH.SD08** Stream processing
- [ ] **TH.SD09** CDN and multi-region
- [ ] **TH.SD10** Paper designs: URL shortener, chat, taxi
- [ ] **TH.SD11** Design doc: 100× more tenants

## Software design (from stage 2; Architecture Patterns with Python)

- [ ] **TH.SW01** Service layer, repository, UoW: what each isolates and costs
- [ ] **TH.SW02** DI and IoC: `Depends` vs container
- [ ] **TH.SW03** SOLID with one project example per principle
- [ ] **TH.SW04** DRY, KISS, YAGNI and their limits
- [ ] **TH.SW05** Coupling, cohesion, separation of concerns, bounded contexts
- [ ] **TH.SW06** Code smells, technical debt, boilerplate, refactoring under tests
- [ ] **TH.SW07** Domain model: entities, value objects, aggregates, invariants
- [ ] **TH.SW08** Hexagonal / ports and adapters / clean architecture
- [ ] **TH.SW09** CQRS and event sourcing: why not event-sourced (ADR)

## Web and API design (stages 0, 1, 9, 17)

- [ ] **TH.WEB01** Request lifecycle: ASGI, middleware, dependencies, handlers
- [ ] **TH.WEB02** REST vs RPC vs GraphQL; status codes; error format
- [ ] **TH.WEB03** Serialization/validation: Pydantic v2, DRF serializers
- [ ] **TH.WEB04** Versioning, backward compatibility, breaking changes
- [ ] **TH.WEB05** Rate limiting vs throttling: algorithms and placement
- [ ] **TH.WEB06** Polling, long polling, SSE, WebSocket, webhooks
- [ ] **TH.WEB07** CORS and preflight; cookies vs bearer tokens and CSRF

## Testing (from stage 0)

- [ ] **TH.TS01** Test pyramid: unit, integration, e2e, smoke, regression
- [ ] **TH.TS02** Test doubles: fake, stub, mock, spy, patch
- [ ] **TH.TS03** Fixtures: scope, factories, rollback per test, dependency overrides
- [ ] **TH.TS04** Coverage as a signal; mutation testing
- [ ] **TH.TS05** Flaky tests: time, ordering, shared state
- [ ] **TH.TS06** Contract tests (Pact), property-based tests (hypothesis)
- [ ] **TH.TS07** Load, stress, soak tests; benchmarks

## Security (stage 1 onward; OWASP)

- [ ] **TH.SEC01** AuthN vs AuthZ; sessions vs tokens; refresh rotation
- [ ] **TH.SEC02** RBAC vs ABAC; least privilege
- [ ] **TH.SEC03** OAuth 2.0 / OIDC; JWT pitfalls; JWKS rotation
- [ ] **TH.SEC04** Hashing: Argon2, salt, pepper; OTP/PIN limits
- [ ] **TH.SEC05** Injection, XSS/CSP, CSRF, SSRF, open redirect, mass assignment
- [ ] **TH.SEC06** Secret management and rotation; encryption at rest; PII in logs
- [ ] **TH.SEC07** Threat model: refund flow and supplier portal boundary

## Django and ORM (stages 15, 22, 24)

- [ ] **TH.DJ01** Django ORM vs SQLAlchemy: QuerySet laziness, select_related vs prefetch_related
- [ ] **TH.DJ02** annotate, aggregate, F/Q, Subquery, raw SQL, RunSQL
- [ ] **TH.DJ03** Migrations: Django vs Alembic; expand/contract
- [ ] **TH.DJ04** Signals and why the service layer instead
- [ ] **TH.DJ05** WSGI vs ASGI for Django
- [ ] **TH.DJ06** DRF: serializers, ViewSets, permissions, throttling, pagination

## Networking and Linux (stages 0, 12, 18, 21)

- [ ] **TH.NET01** TCP handshake, retransmission, keep-alive
- [ ] **TH.NET02** DNS
- [ ] **TH.NET03** TLS handshake and certificates
- [ ] **TH.NET04** HTTP/1.1 vs 2 vs 3; WebSocket protocol
- [ ] **TH.NET05** Processes, threads, signals
- [ ] **TH.NET06** Containers: namespaces, cgroups
- [ ] **TH.NET07** Debugging tools: ps, top, ss, lsof, strace, tcpdump, curl -v

## Algorithms (regularly)

- [ ] **TH.AL01** Arrays, hash maps, two pointers, sliding window
- [ ] **TH.AL02** Stacks, queues, heaps
- [ ] **TH.AL03** Binary search
- [ ] **TH.AL04** Trees, BFS, DFS
- [ ] **TH.AL05** Graph basics
- [ ] **TH.AL06** Dynamic programming basics

## Data engineering (stages 34–37; Fundamentals of Data Engineering, Kimball, DDIA 10–11, Learning Spark)

- [ ] **TH.DE01** OLTP vs OLAP; warehouse vs lake vs lakehouse vs mart
- [ ] **TH.DE02** Medallion architecture: what each layer promises
- [ ] **TH.DE03** Dimensional modelling: facts, dimensions, grain, star vs snowflake, SCD 1/2/3, surrogate and conformed keys, additivity
- [ ] **TH.DE04** Parquet / ORC / Avro; Iceberg / Delta / Hudi: ACID on object storage, time travel, evolution
- [ ] **TH.DE05** ETL vs ELT, batch vs streaming, incremental vs full, upsert/MERGE, idempotency, backfill
- [ ] **TH.DE06** CDC: logical replication, Debezium, slots and WAL; outbox vs CDC
- [ ] **TH.DE07** Orchestration: DAGs, intervals, sensors, SLAs; Airflow vs Dagster vs Prefect
- [ ] **TH.DE08** dbt: models, refs, incremental strategies, snapshots, tests, docs, slim CI
- [ ] **TH.DE09** Spark: architecture, lazy evaluation, plans, shuffle, skew, broadcast join, caching, UDF cost; Hadoop/HDFS history; Polars/DuckDB
- [ ] **TH.DE10** Streaming: event vs processing time, windows, watermarks, state and checkpoints, exactly-once, backpressure; Flink vs Spark SS; Lambda vs Kappa
- [ ] **TH.DE11** Quality and governance: dimensions, contracts, registry, evolution, dedup, quarantine, catalog, lineage, PII, warehouse RBAC, freshness SLOs
- [ ] **TH.DE12** Cloud mapping table: MinIO/Iceberg/Spark/Airflow/Debezium ↔ AWS, GCP, Azure, Databricks, Snowflake

## Machine learning (stages 38–40; Géron, Huyen, ISLR)

- [ ] **TH.ML01** Learning types: supervised, unsupervised, semi-, self-supervised, reinforcement
- [ ] **TH.ML02** Splits and CV (k-fold, stratified, time series); leakage and point-in-time correctness
- [ ] **TH.ML03** Bias-variance, over/underfitting, regularisation (L1, L2, elastic net, early stopping), learning curves
- [ ] **TH.ML04** Loss functions, gradient descent, optimisers (SGD, momentum, Adam, AdamW), LR schedules, batch size, epochs
- [ ] **TH.ML05** Classical models and when: linear/logistic, trees, random forest, boosting (XGBoost, LightGBM, CatBoost), SVM, k-NN, naive Bayes; bagging/boosting/stacking
- [ ] **TH.ML06** Clustering (k-means, DBSCAN, hierarchical) and reduction (PCA, t-SNE, UMAP)
- [ ] **TH.ML07** Metrics: classification, regression, ranking; calibration and thresholds; when accuracy lies
- [ ] **TH.ML08** Class imbalance: weights, oversampling, SMOTE inside the fold
- [ ] **TH.ML09** Feature engineering: encodings, scaling, imputation, selection, SHAP; feature stores
- [ ] **TH.ML10** Hyperparameter tuning: grid, random, Bayesian (Optuna)
- [ ] **TH.ML11** Deep learning essentials: layers, activations, backprop, vanishing/exploding gradients, dropout, norms, CNN, RNN/LSTM/GRU, Transformer/attention, embeddings, transfer learning, PyTorch, Hugging Face
- [ ] **TH.ML12** Time-series forecasting: baselines, ETS, lags, backtests, intermittent demand, hierarchy
- [ ] **TH.ML13** Recommenders: popularity, co-occurrence, item-item, ALS, implicit feedback, cold start, LTR, position bias

## Statistics and mathematics (alongside stages 38 and 40; Practical Statistics, Kohavi)

- [ ] **TH.ST01** Descriptive stats: mean vs median, variance, SD, percentiles, outliers
- [ ] **TH.ST02** Distributions: normal, binomial, Poisson, negative binomial, log-normal, exponential
- [ ] **TH.ST03** Probability: conditional, Bayes' theorem, independence
- [ ] **TH.ST04** Hypothesis testing: p-value, CI, type I/II errors, power, z/t tests, bootstrap, multiple comparisons, peeking
- [ ] **TH.ST05** Correlation vs causation, confounders, holdouts and uplift
- [ ] **TH.ST06** Linear algebra: vectors, dot product, cosine, matrices, factorisation, eigenvalues
- [ ] **TH.ST07** Calculus: derivatives, gradients, chain rule; boosting as gradient descent

## MLOps (stages 39–41; Huyen, Reliable ML, Rules of ML)

- [ ] **TH.MO01** ML lifecycle and where projects die
- [ ] **TH.MO02** Tracking, registry, versioning (MLflow); data versioning (Iceberg snapshots, DVC); reproducibility
- [ ] **TH.MO03** Serving: batch vs online, REST vs gRPC, signatures, ONNX, quantization, pruning, distillation; TorchServe/Triton/BentoML/KServe
- [ ] **TH.MO04** Latency and throughput budgets, batching, CPU vs GPU, data vs model parallelism
- [ ] **TH.MO05** Training-serving skew and feature stores
- [ ] **TH.MO06** Deployment: shadow, canary, A/B; rollback through the registry
- [ ] **TH.MO07** Monitoring: infra, data drift (PSI, KS), concept drift, quality with delayed labels, prediction logs, model cards
- [ ] **TH.MO08** Retraining: scheduled vs triggered, approval vs auto; Kubeflow / SageMaker / Vertex / Airflow trade-offs
- [ ] **TH.MO09** LLM ops: adapters, token and cost budgets, prompt versioning, golden sets, LLM-as-a-judge, prompt injection, tenant-safe retrieval, tool calling with approvals
- [ ] **TH.MO10** Responsible ML: fairness per segment, explainability, privacy, what the audit log must hold
