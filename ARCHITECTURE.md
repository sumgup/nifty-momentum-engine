# Architecture

## Folder Structure

```text
src/momentum_engine/
  cli/                  # CLI commands and command routing
  core/                 # Config loading and shared core utilities
  data/                 # Market data fetch + time-series resampling
  decision/             # Decision/audit report generation for live output
  execution/            # Reserved for execution adapters (currently minimal)
  portfolio/            # Portfolio construction and weighting logic
  ranking/              # Cross-sectional ranking logic
  research/             # Backtest, performance metrics, snapshot analysis
  signals/              # Signal definitions (momentum formula)
  universe/             # Universe loaders (CSV / specific universe helpers)
  engine.py             # LiveMomentumEngine orchestration
```

## Module Responsibilities

- `cli/main.py`
  - Exposes `backtest`, `snapshot`, and `run-live` commands.
  - Maps universe shortcuts and prints outputs.

- `core/config.py`
  - Loads YAML configuration for research/live runs.

- `data/yahoo_fetcher.py`
  - Downloads daily data from Yahoo (`auto_adjust=True`) and returns adjusted close series.

- `data/resampler.py`
  - Converts daily prices to month-end prices with `.resample("ME").last()`.

- `signals/momentum_12_1.py`
  - Computes 12-1 momentum: `Price(t-skip) / Price(t-lookback-skip) - 1`.

- `ranking/cross_sectional_ranker.py`
  - Sorts signal values descending for cross-sectional ranking.

- `portfolio/equal_weight.py`
  - Selects top `N` ranked names and applies equal weights.

- `research/backtester.py`
  - End-to-end research simulation:
  - universe -> data -> monthly -> quarterly rebalance -> signal/rank/select -> returns.

- `research/performance.py`
  - Computes CAGR, annualized volatility, Sharpe, max drawdown.

- `research/snapshot.py`
  - Produces current cross-sectional snapshot with MOM_12_1 + trailing return columns.

- `decision/decision_report.py`
  - Produces full decision trace table (rank, selected flag, cutoff).

- `engine.py`
  - Live pipeline orchestrator (`LiveMomentumEngine`) for decision output and final weights.

- `universe/csv_universe.py` and `universe/nifty100.py`
  - Universe constituent loading and ticker normalization (`.NS`).

## Research vs Snapshot vs Live Pipelines

### Research (`momentum backtest`)
1. Load config and universe (`CSVUniverse`).
2. Fetch adjusted daily prices (`YahooPriceFetcher`).
3. Resample to month-end (`MonthlyResampler`).
4. Generate quarter-end rebalance dates.
5. At each rebalance date:
   - Compute momentum on history up to that date.
   - Rank cross-section.
   - Select top `N` and assign equal weights.
6. Compute period return to next rebalance and update capital.
7. Compute performance metrics.

### Snapshot (`momentum snapshot`)
1. Load chosen universe.
2. Fetch adjusted daily prices.
3. Resample to month-end.
4. Compute latest MOM_12_1.
5. Compute 1M/3M/12M/36M/60M trailing returns.
6. Sort by MOM_12_1 and export snapshot table.

### Live (`momentum run-live`)
1. Load live config.
2. Load live universe (`Nifty100Universe`).
3. Fetch adjusted daily prices.
4. Resample to month-end.
5. Compute MOM_12_1.
6. Rank and select top `N`.
7. Apply equal weights.
8. Generate and save decision report CSV.

## Signal Flow Diagram

```text
Universe Loader
    |
    v
YahooPriceFetcher (daily adjusted prices)
    |
    v
MonthlyResampler (month-end)
    |
    v
Momentum12_1 (signal)
    |
    v
CrossSectionalRanker (descending)
    |
    v
EqualWeightPortfolio (top N + weights)
    |
    +--> Research: backtest return path + PerformanceAnalyzer
    |
    +--> Snapshot: tabular diagnostics (MOM + trailing returns)
    |
    +--> Live: DecisionReport + output/live CSV
```

## Where Selection Logic Lives

- Primary selection point: `src/momentum_engine/portfolio/equal_weight.py`
  - `construct(ranked, top_n)` slices `ranked[:top_n]`.
- Ranking order is created in: `src/momentum_engine/ranking/cross_sectional_ranker.py`.
- Decision trace of selected vs not selected is materialized in: `src/momentum_engine/decision/decision_report.py`.

## Where Portfolio Weighting Is Applied

- Weight assignment is applied in: `src/momentum_engine/portfolio/equal_weight.py`.
- Both Research and Live call this same constructor after ranking.
- Current policy is static equal weight: `1 / top_n` for each selected name.
