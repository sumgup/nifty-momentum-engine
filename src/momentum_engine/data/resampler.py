import pandas as pd


class MonthlyResampler:
    """
    Converts daily price data to month-end prices.
    """

    @staticmethod
    def to_monthly(prices: pd.DataFrame) -> pd.DataFrame:
        return prices.resample("ME").last()