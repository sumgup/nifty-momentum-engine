import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path

from momentum_engine.data.yahoo_fetcher import YahooPriceFetcher
from momentum_engine.data.resampler import MonthlyResampler
from momentum_engine.signals.momentum_12_1 import Momentum12_1


class MomentumDiagnostics:
    """
    Build a multi-section HTML diagnostics report for selected live holdings.

    Each section contains:
    - Full monthly price history (2010-present)
    - Full historical 12-1 momentum history
    - Latest month highlight
    - Current rank and latest MOM_12_1 value
    """

    def __init__(self, selected_tickers: list[str], ranked_signal: pd.Series, output_directory: str):
        self.selected_tickers = selected_tickers
        self.ranked_signal = ranked_signal
        self.output_directory = Path(output_directory)

    def _compute_full_momentum_series(
        self,
        monthly_prices: pd.DataFrame,
        lookback: int = 12,
        skip: int = 1,
    ) -> pd.DataFrame:
        """
        Vectorized full 12-1 momentum history.

        Formula matches Momentum12_1.compute():
        monthly.shift(skip) / monthly.shift(lookback + skip) - 1
        """
        signal_model = Momentum12_1(lookback=lookback, skip=skip)
        return (
            monthly_prices.shift(signal_model.skip)
            / monthly_prices.shift(signal_model.lookback + signal_model.skip)
            - 1
        )

    def _rank_of(self, ticker: str) -> int | None:
        if ticker not in self.ranked_signal.index:
            return None
        return int(self.ranked_signal.index.get_loc(ticker)) + 1

    def _build_price_chart(self, ticker: str, series: pd.Series) -> go.Figure:
        latest_date = series.index[-1]
        latest_value = series.iloc[-1]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series.values,
                mode="lines",
                name="Monthly Price",
                line=dict(width=2),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[latest_date],
                y=[latest_value],
                mode="markers",
                name="Latest",
                marker=dict(size=10, symbol="circle"),
            )
        )

        fig.update_layout(
            title=f"{ticker} - Monthly Price (2010-present)",
            xaxis_title="Date",
            yaxis_title="Price",
            margin=dict(l=40, r=20, t=50, b=40),
            height=360,
            template="plotly_white",
        )

        return fig

    def _build_momentum_chart(self, ticker: str, series: pd.Series) -> go.Figure:
        latest_date = series.index[-1]
        latest_value = series.iloc[-1]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series.values,
                mode="lines",
                name="MOM_12_1",
                line=dict(width=2),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[latest_date],
                y=[latest_value],
                mode="markers",
                name="Latest",
                marker=dict(size=10, symbol="diamond"),
            )
        )
        fig.add_hline(y=0, line_width=1, line_dash="dash")

        fig.update_layout(
            title=f"{ticker} - 12-1 Momentum History",
            xaxis_title="Date",
            yaxis_title="MOM_12_1",
            margin=dict(l=40, r=20, t=50, b=40),
            height=320,
            template="plotly_white",
        )

        return fig

    def generate(self) -> str:
        if not self.selected_tickers:
            raise ValueError("No selected tickers provided for diagnostics.")

        self.output_directory.mkdir(parents=True, exist_ok=True)

        prices = YahooPriceFetcher.fetch(self.selected_tickers, start_date="2010-01-01")
        monthly = MonthlyResampler.to_monthly(prices)
        momentum_history = self._compute_full_momentum_series(monthly, lookback=12, skip=1)

        # Always render sections in explicit rank order (1 -> N).
        selected_set = set(self.selected_tickers)
        ranked_selected = [ticker for ticker in self.ranked_signal.index if ticker in selected_set]

        sections: list[str] = []
        include_plotlyjs = True

        for ticker in ranked_selected:
            if ticker not in monthly.columns:
                continue

            price_series = monthly[ticker].dropna()
            momentum_series = momentum_history[ticker].dropna() if ticker in momentum_history.columns else pd.Series(dtype=float)

            if price_series.empty or momentum_series.empty:
                continue

            current_rank = self._rank_of(ticker)
            current_momentum = self.ranked_signal[ticker] if ticker in self.ranked_signal.index else float("nan")

            price_fig = self._build_price_chart(ticker, price_series)
            momentum_fig = self._build_momentum_chart(ticker, momentum_series)

            price_html = pio.to_html(
                price_fig,
                full_html=False,
                include_plotlyjs=include_plotlyjs,
                default_height="360px",
            )
            include_plotlyjs = False

            momentum_html = pio.to_html(
                momentum_fig,
                full_html=False,
                include_plotlyjs=False,
                default_height="320px",
            )

            rank_text = "NA" if current_rank is None else str(current_rank)
            mom_text = f"{current_momentum:.4f}" if pd.notna(current_momentum) else "NA"

            section = f"""
<section class=\"ticker-section\">
  <h2>{ticker}</h2>
  <p class=\"meta\">Current Rank: {rank_text} | Current MOM_12_1: {mom_text}</p>
  <div class=\"chart\">{price_html}</div>
  <div class=\"chart\">{momentum_html}</div>
</section>
"""
            sections.append(section)

        html = f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Momentum Diagnostics</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; background: #fafafa; color: #111; }}
    h1 {{ margin-bottom: 4px; }}
    .sub {{ color: #555; margin-bottom: 24px; }}
    .ticker-section {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-bottom: 20px; }}
    .ticker-section h2 {{ margin: 0 0 4px 0; }}
    .meta {{ margin: 0 0 10px 0; color: #333; font-size: 14px; }}
    .chart {{ margin-bottom: 8px; }}
  </style>
</head>
<body>
  <h1>Momentum Diagnostics Report</h1>
  <p class=\"sub\">Selected tickers with monthly price and full 12-1 momentum history.</p>
  {''.join(sections)}
</body>
</html>
"""

        output_path = self.output_directory / "momentum_diagnostics.html"
        output_path.write_text(html, encoding="utf-8")

        return str(output_path)
