import pandas as pd
import numpy as np


class PerformanceAnalyzer:

    @staticmethod
    def compute_metrics(results: pd.DataFrame) -> dict:
        """
        Compute performance statistics from backtest results.
        Expects results to contain:
        - capital
        - portfolio_return
        - next_date
        """

        df = results.copy()
        df = df.sort_values("next_date")

        # Compute periodic returns
        returns = df["portfolio_return"]

        # CAGR
        start_cap = df["capital"].iloc[0]
        end_cap = df["capital"].iloc[-1]
        n_years = (df["next_date"].iloc[-1] - df["next_date"].iloc[0]).days / 365.25

        cagr = (end_cap / start_cap) ** (1 / n_years) - 1 if n_years > 0 else 0

        # Annualized Volatility (quarterly → 4 periods per year)
        ann_vol = returns.std() * np.sqrt(4)

        # Sharpe Ratio (risk-free assumed 0)
        sharpe = (returns.mean() / returns.std()) * np.sqrt(4) if returns.std() != 0 else 0

        # Max Drawdown
        equity_curve = df["capital"]
        running_max = equity_curve.cummax()
        drawdown = (equity_curve - running_max) / running_max
        max_dd = drawdown.min()

        return {
            "CAGR": cagr,
            "Annualized Volatility": ann_vol,
            "Sharpe Ratio": sharpe,
            "Max Drawdown": max_dd
        }

    @staticmethod
    def compute_drawdown_series(results: pd.DataFrame) -> pd.Series:
        equity_curve = results.sort_values("next_date")["capital"]
        running_max = equity_curve.cummax()
        drawdown = (equity_curve - running_max) / running_max
        return drawdown