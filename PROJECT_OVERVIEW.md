# Nifty Momentum Engine — Project Overview

## 1. What Is This Project?

The Nifty Momentum Engine is a modular, configuration-driven quantitative research and portfolio construction system built for Indian equity indices.

It implements:

- Cross-sectional 12–1 momentum
- Quarterly rebalancing
- Equal-weight top-N portfolio construction
- CLI-based research and live execution modes
- Multi-universe support via CSV input

This project separates:

Research (strategy development)
from
Live Execution (portfolio generation)

It is designed to be extended into a production-grade quantitative framework.

---

## 2. Core Strategy Logic

The engine implements classical cross-sectional momentum:

1. Define a universe (e.g., Nifty100).
2. Fetch adjusted price data (Yahoo Finance).
3. Convert daily prices to monthly.
4. Compute 12–1 momentum:
   (Price[t-1] / Price[t-12-1]) - 1
5. Rank stocks descending.
6. Select top N.
7. Equal weight allocation.

There are currently:

- No sector constraints
- No volatility adjustment
- No absolute momentum filter
- No transaction cost modeling
- No survivorship bias adjustment

This is a pure momentum prototype.

---

## 3. Architecture Overview

High-level flow:

Universe → Price Data → Signal → Ranking → Portfolio → Performance

CLI entry points:

- `momentum backtest` → Research Mode
- `momentum run-live` → Live Mode
- `momentum snapshot` → Cross-sectional inspection

Configuration files:

- `config/research.yaml` → Backtest configuration
- `config/live.yaml` → Live portfolio configuration

---

## 4. Modes of Operation

### Research Mode

Used to:

- Test strategy performance over time
- Adjust parameters
- Compare universes
- Evaluate risk and return metrics

Command:
poetry run momentum backtest


Outputs:

- CAGR
- Annualized Volatility
- Sharpe Ratio
- Max Drawdown
- Backtest CSV saved in `output/research/`

---

### Snapshot Mode

Used to:

- View entire universe ranked
- Inspect 1M, 3M, 12M, 36M, 60M returns
- Understand dispersion structure

Command:
poetry run momentum run-live


Outputs:

- Selected stocks
- Weight allocation
- File saved in `output/live/`

This does NOT auto-trade.
Execution must be done manually.

---

## 5. Adding a New Universe

1. Download constituents from NSE website.
2. Save CSV in:

Outputs:

- Selected stocks
- Weight allocation
- File saved in `output/live/`

This does NOT auto-trade.
Execution must be done manually.

---

## 5. Adding a New Universe

1. Download constituents from NSE website.
2. Save CSV in:

3. (Optional) Add shortcut in CLI:
UNIVERSE_SHORTCUTS = {
"n500": "data/nifty500_constituents.csv",
}

4. Run:

Universe CSV must:

- Contain a "Symbol" column (NSE format)
OR
- Be a single-column ticker list

---

## 6. What Is Currently Working

- Modular architecture
- Config-driven strategy
- Multi-universe support
- CLI override of universes
- Snapshot inspection tool
- Performance metric calculation
- Clean output structure
- Reproducible research workflow

---

## 7. Known Limitations

This is currently a research prototype.

Limitations include:

1. No transaction cost modeling
2. No slippage modeling
3. No turnover reporting
4. Static universe (survivorship bias present)
5. No benchmark comparison
6. No risk constraints
7. No local data caching
8. Yahoo Finance dependency
9. No automated execution layer

Performance results are optimistic because costs and survivorship bias are not handled.

---

## 8. What Needs Improvement (Priority Order)

### High Priority

- Add transaction cost modeling
- Add portfolio turnover calculation
- Add benchmark comparison (alpha, information ratio)

### Medium Priority

- Add absolute momentum filter
- Add volatility column in snapshot
- Add sector exposure analysis
- Add drawdown curve export

### Advanced / Institutional

- Historical index membership (remove survivorship bias)
- Local price data caching
- Parameter robustness testing framework
- Multi-universe comparison command
- Risk management overlay
- Logging and rebalance history tracking

---

## 9. Intended Use Cases

This project can evolve into:

- A personal quant research lab
- A systematic trading framework
- A publishable research engine
- A foundation for capital deployment

Current state:
Advanced research prototype.

---

## 10. Mental Model for Using This Project

Research Mode = Laboratory  
Snapshot Mode = Microscope  
Backtest = Time Machine  
Live Mode = Portfolio Generator  

Universe CSV = Boundary of the world  
Momentum rule = Selection logic  
Top N = Portfolio constraint  

---

## 11. If Deploying Real Capital

Before deploying:

- Add cost modeling
- Validate robustness
- Add benchmark comparison
- Evaluate drawdown tolerance
- Confirm operational discipline

This engine currently supports research.
Institutional deployment requires additional layers.

---

## 12. Long-Term Vision

Transform from:

Momentum Script

Into:

Research Framework  
→ Portfolio Construction Engine  
→ Risk-Controlled Capital System

---

END
