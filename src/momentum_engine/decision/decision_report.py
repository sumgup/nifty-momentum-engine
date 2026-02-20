import pandas as pd


class DecisionReport:
    """
    Generates full decision trace for a rebalance.
    """

    @staticmethod
    def generate(signal: pd.Series, ranked: pd.Series, top_n: int) -> pd.DataFrame:
        df = pd.DataFrame({
            "ticker": ranked.index,
            "momentum_12_1": ranked.values
        })

        df["rank"] = range(1, len(df) + 1)
        df["cutoff_rank"] = top_n
        df["selected"] = df["rank"] <= top_n
        df["universe_size"] = len(signal)

        return df