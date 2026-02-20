from pathlib import Path
import pandas as pd


class Nifty100Universe:
    """
    Loads Nifty100 constituents directly from NSE download CSV.
    Automatically converts Symbol column to Yahoo format (.NS).
    """

    @staticmethod
    def get_tickers() -> list[str]:
        path = Path("data/nifty100_constituents.csv")

        if not path.exists():
            raise FileNotFoundError("Nifty100 CSV file not found in data/ directory.")

        df = pd.read_csv(path)

        if "Symbol" not in df.columns:
            raise ValueError("CSV must contain 'Symbol' column.")

        tickers = df["Symbol"].dropna().unique().tolist()

        # Convert to Yahoo Finance format
        tickers = [f"{symbol}.NS" for symbol in tickers]

        return tickers