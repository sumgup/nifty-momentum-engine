
# 📄 RUN.md

````markdown
# Nifty Momentum Engine — Run Guide

This document explains how to:

- Install and run the project
- Backtest strategies
- Add new index universes
- Override universes via CLI
- Modify strategy parameters
- Understand outputs

---

# 1️⃣ Initial Setup

## Install dependencies

```bash
poetry install
````

Optional (activate environment):

```bash
poetry shell
```

---

# 2️⃣ Run Backtest (Default)

Uses:

* config/research.yaml
* Universe defined inside config

```bash
poetry run momentum backtest
```

---

# 3️⃣ Run Backtest with Universe Shortcut

Available CLI shortcuts (defined in main.py):

| Shortcut | CSV File                       |
| -------- | ------------------------------ |
| n100     | data/nifty100_constituents.csv |
| n200     | data/nifty200_constituents.csv |
| next50   | data/ind_niftynext50list.csv   |

Example:

```bash
poetry run momentum backtest -u n100
poetry run momentum backtest -u next50
```

---

# 4️⃣ Run Backtest with Custom Universe File

```bash
poetry run momentum backtest -u data/my_custom_universe.csv
```

CSV must either:

* Contain a column named `Symbol` (NSE format)
  OR
* Be a single-column ticker list

---

# 5️⃣ Understanding CLI Output

Example:

```
Backtest complete.
Universe: nifty100_constituents
Universe size: 100

Performance Metrics:
CAGR: 28.41%
Annualized Volatility: 22.98%
Sharpe Ratio: 1.21
Max Drawdown: -22.96%
```

Metrics reported:

* CAGR (%)
* Annualized Volatility (%)
* Sharpe Ratio
* Max Drawdown (%)

---

# 6️⃣ Where Results Are Saved

Backtest CSV:

```
output/research/
```

Live decision files:

```
output/live/
```

---

# 7️⃣ Add a New Universe

## Step 1 — Download Constituents

Download index constituents from NSE website.

## Step 2 — Place CSV File

Put file in:

```
data/
```

Example:

```
data/nifty500_constituents.csv
```

## Step 3 — (Optional) Add CLI Shortcut

Edit:

```
src/momentum_engine/cli/main.py
```

Inside:

```python
UNIVERSE_SHORTCUTS = {
    "n500": "data/nifty500_constituents.csv",
}
```

Now run:

```bash
poetry run momentum backtest -u n500
```

---

# 8️⃣ Modify Strategy Parameters

Edit:

```
config/research.yaml
```

Adjust:

* start_date
* end_date
* lookback_months
* skip_recent_months
* top_n

Then rerun:

```bash
poetry run momentum backtest
```

---

# 9️⃣ Run Live Selection

```bash
poetry run momentum run-live
```

Outputs:

* Decision CSV in output/live/
* Equal-weight top N portfolio

---

# 🔟 Common Debug Checks

## Check Universe Size

If results look identical across universes:

Add debug inside Backtester:

```python
print(f"Universe size: {len(self.universe)}")
```

Ensure different universes produce different sizes.

---

## Check Duplicate Symbols

If universe size is incorrect:

* Open CSV
* Remove duplicate rows
* Remove blank rows

---

## Yahoo Data Issues

If download fails:

* Check internet connection
* Large universes may take longer
* Yahoo may throttle large batches

---

# 1️⃣1️⃣ Known Assumptions

* Dividends included (Yahoo adjusted prices)
* No transaction costs
* No slippage
* Static universe (survivorship bias present)

---

# 1️⃣2️⃣ Architecture Overview

CLI → Engine → Data → Signal → Ranking → Portfolio → Performance

Universe selection:

* Defined in config
* Overrideable via CLI
* Shortcut supported

---

# 1️⃣3️⃣ Next Potential Enhancements

* Transaction cost modeling
* Turnover tracking
* Benchmark comparison
* Multi-universe comparison command
* Historical membership (remove survivorship bias)

---

END

```

---
