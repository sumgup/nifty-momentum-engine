import yfinance as yf
import pandas as pd


class YahooPriceFetcher:
    """
    Fetches adjusted daily price data from Yahoo Finance.
    """

    @staticmethod
    def fetch(tickers: list[str], start_date: str) -> pd.DataFrame:
        data = yf.download(
            tickers,
            start=start_date,
            auto_adjust=True,
            progress=False,
        )

        if "Close" not in data:
            raise ValueError("Close prices not found in Yahoo response.")

        return data["Close"]