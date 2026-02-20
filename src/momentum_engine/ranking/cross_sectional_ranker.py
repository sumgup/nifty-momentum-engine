import pandas as pd


class CrossSectionalRanker:
    """
    Ranks stocks by descending signal value.
    """

    @staticmethod
    def rank(signal: pd.Series) -> pd.Series:
        return signal.sort_values(ascending=False)