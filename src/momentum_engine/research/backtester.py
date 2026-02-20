import pandas as pd
from pathlib import Path

from momentum_engine.core.config import ConfigLoader
from momentum_engine.universe.nifty100 import Nifty100Universe
from momentum_engine.data.yahoo_fetcher import YahooPriceFetcher
from momentum_engine.data.resampler import MonthlyResampler
from momentum_engine.signals.momentum_12_1 import Momentum12_1
from momentum_engine.ranking.cross_sectional_ranker import CrossSectionalRanker
from momentum_engine.portfolio.equal_weight import EqualWeightPortfolio


class Backtester:

    def __init__(self, config_path: str):
        self.config = ConfigLoader(config_path).load()

        self.start = pd.to_datetime(self.config["backtest"]["start_date"])
        self.end = pd.to_datetime(self.config["backtest"]["end_date"])
        self.initial_capital = self.config["backtest"]["initial_capital"]

        self.universe = Nifty100Universe.get_tickers()

        self.lookback = self.config["momentum"]["lookback_months"]
        self.skip = self.config["momentum"]["skip_recent_months"]
        self.top_n = self.config["portfolio"]["top_n"]

    def run(self) -> pd.DataFrame:

        # -------------------------
        # 1. Fetch & prepare data
        # -------------------------

        prices = YahooPriceFetcher.fetch(
            self.universe,
            start_date=self.start.strftime("%Y-%m-%d")
        )

        monthly = MonthlyResampler.to_monthly(prices)

        # Restrict to backtest window
        monthly = monthly.loc[
            (monthly.index >= self.start) &
            (monthly.index <= self.end)
        ]

        # -------------------------
        # 2. Generate quarterly rebalance dates
        # -------------------------

        rebalance_dates = monthly.resample("QE").last().index

        capital = self.initial_capital
        portfolio_history = []

        # -------------------------
        # 3. Loop through rebalance periods
        # -------------------------

        for i in range(len(rebalance_dates) - 1):

            date = rebalance_dates[i]
            next_rebalance_date = rebalance_dates[i + 1]

            # Ensure enough lookback history exists
            if date < monthly.index[0] + pd.DateOffset(months=self.lookback + self.skip):
                continue

            # -------------------------
            # Compute momentum signal
            # -------------------------

            signal = Momentum12_1(
                self.lookback,
                self.skip
            ).compute(monthly.loc[:date])

            ranked = CrossSectionalRanker.rank(signal)

            weights = EqualWeightPortfolio.construct(
                ranked.index.tolist(),
                self.top_n
            )

            # -------------------------
            # Compute portfolio return over full quarter
            # -------------------------

            current_prices = monthly.loc[date]
            next_prices = monthly.loc[next_rebalance_date]

            portfolio_return = 0.0

            for ticker, weight in weights.items():
                if ticker in current_prices and ticker in next_prices:
                    ret = (next_prices[ticker] / current_prices[ticker]) - 1
                    portfolio_return += ret * weight

            capital *= (1 + portfolio_return)

            portfolio_history.append({
                "rebalance_date": date,
                "next_date": next_rebalance_date,
                "portfolio_return": portfolio_return,
                "capital": capital
            })

        results_df = pd.DataFrame(portfolio_history)

        return results_df