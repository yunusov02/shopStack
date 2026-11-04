# Stage 40: Recommendations, search ranking, experimentation and anomaly detection

Where: `ml/models/recsys`, `ml/models/anomaly`, `modules/experiments` (monolith), `services/ml-serving`. Prerequisites: stages 39 and 17.

## Recommendations `[CORE]`

- [ ] **S40.T01** Baselines: most popular per tenant and per category, co-occurrence "bought together"; ranking metrics (Precision@K, Recall@K, MAP, NDCG) on a held-out time window
  Must know: ranking metrics, implicit feedback

- [ ] **S40.T02** ADR 0076 and item-item collaborative filtering on sparse matrices (`scipy.sparse`); cold-start rules for new products and customers
  Must know: collaborative filtering, cold start

- [ ] **S40.T03** Serving: nightly top-N per customer and per product in Redis; online re-rank removing out-of-stock and applying business rules (margin floor, promo boost); storefront and POS endpoints
  Must know: precomputed recommendations, re-ranking

## Embeddings and vector search `[CORE]`

- [ ] **S40.T04** ADR 0077: embedding source (hosted vs local) and vector store (pgvector vs Qdrant vs OpenSearch k-NN)
  Must know: embeddings, vector databases

- [ ] **S40.T05** Product embeddings pipeline from text; pgvector table with HNSW and IVFFlat compared on recall and latency; cosine vs dot vs L2 note
  Must know: ANN indexes, similarity measures

- [ ] **S40.T06** Hybrid search: stage 10 FTS fused with vector similarity (reciprocal rank fusion); labelled query set including transliterations and misspellings; NDCG@10 vs FTS alone
  Must know: rank fusion, search evaluation

- [ ] **S40.T07** "Similar products" and "did you mean"; index updated from product CDC and `stock.changed` through the platform, never synchronously in the core
  Must know: asynchronous index updates

## Experimentation platform `[CORE]`

- [ ] **S40.T08** ADR 0078 and `modules/experiments`: experiment and variant models, allocation unit (customer / terminal / tenant), consistent hashed assignment, kill switch, `experiment.exposed.v1`
  Must know: A/B infrastructure, consistent assignment

- [ ] **S40.T09** Statistics module: power analysis and sample size, z-test for proportions, Welch's t-test and bootstrap for revenue, p-value with CI, multiple-comparison correction; unit tests against known results
  Must know: hypothesis testing, power

- [ ] **S40.T10** Analysis as a dbt model plus a notebook template; decision record template (ship / stop / iterate); peeking and novelty effects documented; guardrail metrics (refund rate, latency)
  Must know: experiment analysis pitfalls

- [ ] **S40.T11** First three experiments run on seeded traffic: recommender vs most-popular, hybrid vs FTS search, win-back message vs holdout
  Must know: running an experiment end to end

## Anomaly and fraud detection `[CORE]`

- [ ] **S40.T12** Rules baseline on sensitive operations per cashier per shift as a pure function with tests; precision on labelled past incidents (seeded)
  Must know: rule-based scoring

- [ ] **S40.T13** Isolation Forest and robust z-scores on shift features; `anomaly.detected.v1` with evidence; core writes an audit entry and a manager notification, never blocks
  Must know: Isolation Forest, anomaly scoring

- [ ] **S40.T14** Review loop: manager confirms or rejects through the stage 30 workflow; decisions stored as labels; precision at top-10 alerts per day as the metric
  Must know: human-in-the-loop labelling

- [ ] **S40.T15** Tests: recommender beats popularity offline and in a powered A/B; hybrid search ≥ FTS on the labelled set; planted fraudulent cashier in the top ten on day one
  Must know: evaluation harnesses

## Extensions

- [ ] **S40.T16** `[EXT]` Learning to rank (`lambdarank`) with diversity and position-bias notes; image embeddings from stage 23 photos for similarity and category suggestions (suggestion + decision both stored)
  Must know: learning to rank, image embeddings

- [ ] **S40.T17** `[EXT]` CUPED and switchback tests; supervised fraud model on labels with the online score behind a timeout at refund time (step-up PIN when high)
  Must know: variance reduction, online scoring with fallback

- [ ] **S40.T18** `[OPT]` Session-based recommendations; contrastive fine-tuning of embeddings; bandits for banners; time-series anomaly detection for stage 20 alerts
  Must know: bandits, contrastive learning
