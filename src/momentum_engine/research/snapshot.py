import pandas as pd
from pathlib import Path

from momentum_engine.universe.csv_universe import CSVUniverse
from momentum_engine.data.yahoo_fetcher import YahooPriceFetcher
from momentum_engine.data.resampler import MonthlyResampler
from momentum_engine.signals.momentum_12_1 import Momentum12_1


class SnapshotAnalyzer:

    def __init__(self, universe_file: str):
        self.universe_file = universe_file
        self.universe_name = Path(universe_file).stem

        universe_loader = CSVUniverse(universe_file)
        self.tickers = universe_loader.get_tickers()

    def run(self):

        # Fetch daily prices
        prices = YahooPriceFetcher.fetch(
            self.tickers,
            start_date="2010-01-01"
        )

        # Convert to month-end prices
        monthly = MonthlyResampler.to_monthly(prices)

        # Compute 12–1 momentum using official signal class
        momentum_signal = Momentum12_1(
            lookback=12,
            skip=1
        )

        mom_latest = momentum_signal.compute(monthly)

        # Helper function for trailing returns
        def compute_return(months):
            return (monthly.iloc[-1] / monthly.shift(months).iloc[-1]) - 1

        snapshot_df = pd.DataFrame({
            "Ticker": monthly.columns,
            "MOM_12_1": mom_latest.reindex(monthly.columns).values,
            "1M": compute_return(1).values,
            "3M": compute_return(3).values,
            "12M": compute_return(12).values,
            "36M": compute_return(36).values,
            "60M": compute_return(60).values,
        })

        # Drop rows where momentum is NaN
        snapshot_df = snapshot_df.dropna(subset=["MOM_12_1"])

        # Sort by official signal
        snapshot_df = snapshot_df.sort_values(
            "MOM_12_1",
            ascending=False
        )

        snapshot_df.reset_index(drop=True, inplace=True)

        return snapshot_df