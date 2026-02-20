from pathlib import Path
import pandas as pd


class CSVUniverse:
    """
    Generic universe loader from CSV file.
    Expects either:
    - A column named 'Symbol'
    OR
    - Single column of tickers
    """

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def get_tickers(self) -> list[str]:

        if not self.file_path.exists():
            raise FileNotFoundError(f"Universe file not found: {self.file_path}")

        df = pd.read_csv(self.file_path)

        # Case 1: NSE download format
        if "Symbol" in df.columns:
            tickers = df["Symbol"].dropna().unique().tolist()
            tickers = [f"{symbol}.NS" for symbol in tickers]
            return tickers

        # Case 2: Single column format
        if df.shape[1] == 1:
            tickers = df.iloc[:, 0].dropna().unique().tolist()
            return tickers

        raise ValueError("Unsupported CSV format for universe.")