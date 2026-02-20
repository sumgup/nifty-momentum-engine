from datetime import datetime
from pathlib import Path

from momentum_engine.core.config import ConfigLoader
from momentum_engine.universe.nifty100 import Nifty100Universe
from momentum_engine.data.yahoo_fetcher import YahooPriceFetcher
from momentum_engine.data.resampler import MonthlyResampler
from momentum_engine.signals.momentum_12_1 import Momentum12_1
from momentum_engine.ranking.cross_sectional_ranker import CrossSectionalRanker
from momentum_engine.portfolio.equal_weight import EqualWeightPortfolio
from momentum_engine.decision.decision_report import DecisionReport


class LiveMomentumEngine:

    def __init__(self, config_path: str):
        self.config = ConfigLoader(config_path).load()

    def run(self) -> None:
        # Universe
        universe_name = self.config["universe"]["name"]

        if universe_name != "nifty100":
            raise ValueError(f"Unsupported universe: {universe_name}")

        tickers = Nifty100Universe.get_tickers()

        # Data
        start_date = self.config["data"]["start_date"]
        prices = YahooPriceFetcher.fetch(tickers, start_date=start_date)
        monthly = MonthlyResampler.to_monthly(prices)

        # Signal
        lookback = self.config["momentum"]["lookback_months"]
        skip = self.config["momentum"]["skip_recent_months"]
        signal = Momentum12_1(lookback, skip).compute(monthly)

        # Ranking
        ranked = CrossSectionalRanker.rank(signal)

        # Portfolio
        top_n = self.config["portfolio"]["top_n"]
        weights = EqualWeightPortfolio.construct(ranked.index.tolist(), top_n)

        # Decision report
        decision_df = DecisionReport.generate(signal, ranked, top_n)

        output_dir = self.config["output"]["directory"]
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        date_str = datetime.today().strftime("%Y-%m-%d")
        decision_path = f"{output_dir}/{date_str}_decision.csv"
        decision_df.to_csv(decision_path, index=False)

        return weights, decision_path