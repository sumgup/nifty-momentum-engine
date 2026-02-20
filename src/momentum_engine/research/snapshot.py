import pandas as pd
from datetime import datetime
from pathlib import Path

from momentum_engine.universe.csv_universe import CSVUniverse
from momentum_engine.data.yahoo_fetcher import YahooPriceFetcher
from momentum_engine.data.resampler import MonthlyResampler


class SnapshotAnalyzer:

    def __init__(self, universe_file: str):
        self.universe_file = universe_file
        self.universe_name = Path(universe_file).stem

        universe_loader = CSVUniverse(universe_file)
        self.tickers = universe_loader.get_tickers()

    def run(self):

        prices = YahooPriceFetcher.fetch(self.tickers, start_date="2010-01-01")
        monthly = MonthlyResampler.to_monthly(prices)

        latest = monthly.iloc[-1]

        def compute_return(months):
            return (monthly.iloc[-1] / monthly.shift(months).iloc[-1]) - 1

        snapshot_df = pd.DataFrame({
            "Ticker": latest.index,
            "1M": compute_return(1).values,
            "3M": compute_return(3).values,
            "12M": compute_return(12).values,
            "36M": compute_return(36).values,
            "60M": compute_return(60).values,
        })

        snapshot_df = snapshot_df.sort_values("12M", ascending=False)

        return snapshot_df