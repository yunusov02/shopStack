# Stage 38: ML foundations: features, training, evaluation (the first models)

Where: `ml/` (`ml/features`, `ml/pipelines`, `ml/models`), `notebooks/`. Prerequisites: stages 35 and 29.

## Features `[CORE]`

- [ ] **S38.T01** ADR 0070 (own feature tables first, Feast as `[EXT]`) and ADR 0072 (LightGBM vs XGBoost vs CatBoost; the baseline rule)
  Must know: feature stores, gradient boosting libraries

- [ ] **S38.T02** Feature tables in Gold: per variant-location-day (lag sums, days since last sale, price, promo flag, stock-out days, calendar) and per customer-day (RFM, basket size, points, returns share); built by dbt or a Spark job from Airflow
  Must know: feature engineering for retail, RFM

- [ ] **S38.T03** Point-in-time correctness: `feature_timestamp` on every row, as-of join helper with a test proving no future data; SCD2 prices used "as of" sale time
  Must know: as-of joins, point-in-time correctness

- [ ] **S38.T04** Leakage lab: three planted leaks (future feature, full-data target encoding, random split on time series); validation vs backtest scores; checklist in `docs/notes/ml.md`
  Must know: data leakage

- [ ] **S38.T05** `ml/features` transforms (encoding, scaling, imputation with missing flags, selection) as versioned, unit-tested functions; the same code to be reused for serving
  Must know: sklearn transformers, pipelines

## Tracking and reproducibility `[CORE]`

- [ ] **S38.T06** ADR 0071 and MLflow in Compose (Postgres backend, MinIO artifacts); a run logs params, metrics, Iceberg snapshot id, feature set version, git SHA, `uv.lock`
  Must know: MLflow tracking

- [ ] **S38.T07** Reproducibility test: re-running a run id with the same snapshot reproduces metrics; seeds fixed everywhere
  Must know: seeds, determinism

- [ ] **S38.T08** Training as pipelines: `ml/pipelines/<problem>/train.py` with a config file, run from an Airflow DAG; notebooks only for exploration
  Must know: pipeline vs notebook discipline

## Model 1: demand forecast `[CORE]`

- [ ] **S38.T09** Baseline in the pipeline: moving average and ETS (`statsmodels`); rolling-origin backtest; WAPE/sMAPE instead of MAPE at zero; per product class (fast, slow, intermittent)
  Must know: time-series backtesting, forecast metrics

- [ ] **S38.T10** LightGBM global model with lag features; expanding-window time-series CV; comparison vs baseline per class; learning curves, early stopping, regularisation shown
  Must know: gradient boosting, time-series CV, bias-variance

- [ ] **S38.T11** Output as data: `DemandForecast` rows with prediction interval and model version; `forecast.published.v1`; stage 29 planning consumes it and records the model version; model chosen per class by backtest
  Must know: event contracts, consumer side in the core

## Model 2: churn `[CORE]`

- [ ] **S38.T12** Label ADR: "no purchase 60 days after `d`"; non-overlapping feature and label windows; base rate per tenant
  Must know: label design

- [ ] **S38.T13** Logistic regression baseline then LightGBM; stratified k-fold; class weights vs oversampling vs SMOTE inside the fold
  Must know: class imbalance, stratification

- [ ] **S38.T14** Metrics report: precision, recall, F1, ROC-AUC, PR-AUC, confusion matrix, log loss; calibration (reliability curve, isotonic); threshold chosen by business cost
  Must know: classification metrics, calibration, threshold tuning

- [ ] **S38.T15** Explainability: permutation importance and SHAP per prediction; sanity check of top features
  Must know: SHAP

- [ ] **S38.T16** Output as data: `customer_segment.changed.v1` with risk band and model version; core adds a "churn risk" customer group; notification campaign respects stage 14 preferences
  Must know: event consumers, customer groups

## Model 3: segmentation `[CORE]`

- [ ] **S38.T17** K-means on scaled RFM (elbow, silhouette), DBSCAN and hierarchical comparison, PCA for the 2-D plot; segment profiles
  Must know: clustering, PCA

- [ ] **S38.T18** Stable segment labels across runs (`segment_version`, relabelling step) with a test
  Must know: label stability

## Statistics `[CORE]`

- [ ] **S38.T19** Statistics notebook on real data: count distributions (Poisson, negative binomial), log-normal basket values, bootstrap CIs, a first hypothesis test, correlation vs causation example; notes in `docs/notes/stats.md`
  Must know: distributions, bootstrap, hypothesis tests

## Done `[CORE]`

- [ ] **S38.T20** README section with the forecast comparison table, churn calibration per decile, and the leakage lab results
  Must know: reporting ML results honestly

## Extensions

- [ ] **S38.T21** `[EXT]` Feast with Postgres offline and Redis online stores; feature views and materialisation; Optuna tuning; DVC for small labelled sets
  Must know: Feast, Optuna, DVC

- [ ] **S38.T22** `[EXT]` Intermittent demand (Croston/TSB), promotion and holiday features, hierarchical reconciliation; survival analysis for churn; product clustering and association rules
  Must know: intermittent demand, survival analysis, association rules

- [ ] **S38.T23** `[OPT]` LSTM or small Transformer on the same backtest; uplift modelling; embeddings as features
  Must know: sequence models, uplift
