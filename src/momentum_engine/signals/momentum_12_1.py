import pandas as pd


class Momentum12_1:
    """
    Computes 12-1 momentum:
    Return from t-12 to t-1.
    """

    def __init__(self, lookback: int = 12, skip: int = 1):
        self.lookback = lookback
        self.skip = skip

    def compute(self, monthly_prices: pd.DataFrame) -> pd.Series:
        if len(monthly_prices) < self.lookback + self.skip:
            raise ValueError("Not enough data to compute momentum.")

        momentum = (
            monthly_prices.shift(self.skip)
            / monthly_prices.shift(self.lookback + self.skip)
            - 1
        )

        return momentum.iloc[-1].dropna()