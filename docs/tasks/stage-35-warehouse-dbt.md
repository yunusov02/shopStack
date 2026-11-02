# Stage 35: Warehouse modelling and dbt

Where: `data/warehouse` (dbt project), database `shopstack_dw`. Prerequisites: stage 34.

## Dimensional model `[CORE]`

- [ ] **S35.T01** ADR 0063: Postgres as the first warehouse engine, ClickHouse as `[EXT]` serving layer; ADR 0064: grain of every fact table, star vs snowflake
  Must know: star schema, grain

- [ ] **S35.T02** Dimension design doc: `dim_date`, `dim_time_of_day`, `dim_product` (SCD2), `dim_customer` (SCD2), `dim_location` (SCD1), `dim_cashier`, `dim_promotion`, `dim_tenant`; surrogate keys, conformed and role-playing dimensions
  Must know: SCD types, surrogate vs natural keys

- [ ] **S35.T03** Fact design doc: `fact_sale_line`, `fact_stock_movement`, `fact_order`, `fact_journal_line`; additive / semi-additive / non-additive measures marked; degenerate dimensions
  Must know: additivity, degenerate dimensions

- [ ] **S35.T04** `dim_date` and `dim_time_of_day` generated (holidays for Uzbekistan as a seed file)
  Must know: date dimensions

## dbt project `[CORE]`

- [ ] **S35.T05** dbt project skeleton: profiles for dev/CI/prod schemas, `staging` models over Silver sources with `source()` freshness, naming conventions
  Must know: dbt project layout, sources

- [ ] **S35.T06** `dim_product` and `dim_customer` as SCD2 from CDC history (and a dbt snapshot variant for comparison); `is_current`, `valid_from`, `valid_to`
  Must know: dbt snapshots, SCD2 from change logs

- [ ] **S35.T07** `fact_sale_line` incremental model: watermark + late-arrival window, `merge` strategy, dimension keys resolved as-of sale time; agreement with the stage 5 snapshots tested
  Must know: incremental models, as-of joins

- [ ] **S35.T08** Remaining facts (`fact_stock_movement`, `fact_order`, `fact_journal_line`) and Gold aggregates (`agg_daily_sales_by_location`, finance and merchandising marts)
  Must know: aggregate tables, data marts

- [ ] **S35.T09** dbt tests: generic tests on every key; singular tests (debit = credit, sale total = sum of lines, no negative on-hand); CI runs on a sample, nightly in full
  Must know: dbt tests, singular tests

- [ ] **S35.T10** Reconciliation model and report: Gold revenue/COGS/VAT per day = stage 26 ledger to the tiyin; stock on hand = stage 3 ledger; first differing row shown
  Must know: reconciliation queries

- [ ] **S35.T11** Airflow DAG `dbt_build` after Silver lands; slim CI (`state:modified+`); `dbt docs generate` published
  Must know: dbt in orchestration, slim CI

## SQL lab `[CORE]`

- [ ] **S35.T12** Window-function lab on Gold: dedup with `ROW_NUMBER`, `LAG` for days between purchases, running stock with frames, `GROUPING SETS`/`ROLLUP`, recursive CTE for the category tree, correlated subquery vs join with `EXPLAIN`
  Must know: window functions, grouping sets, recursive CTEs

- [ ] **S35.T13** One report in SQL, pandas, Polars and PySpark (after S36) with a note on which to choose at 10K / 10M / 10B rows
  Must know: engine trade-offs

## Done `[CORE]`

- [ ] **S35.T14** End-to-end test: product renamed mid-month shows the old name on old sales; Gold equals the ledger; stage 16 dashboard numbers match Gold
  Must know: integration tests across pipelines

## Extensions

- [ ] **S35.T15** `[EXT]` Snapshot facts (daily stock on hand) and accumulating snapshot fact for orders
  Must know: snapshot and accumulating facts

- [ ] **S35.T16** `[EXT]` ClickHouse as Gold serving: MergeTree keys, materialized views, `Decimal`, dbt-clickhouse; dashboard queries measured on both engines; ADR 0063 completed
  Must know: MergeTree, ClickHouse data types

- [ ] **S35.T17** `[EXT]` Analytics service reads Gold for heavy reports; parallel run and comparison before switching
  Must know: parallel run

- [ ] **S35.T18** `[OPT]` Semantic layer and a BI tool (Metabase or Superset); Data Vault spike and why not
  Must know: metrics layer, Data Vault
