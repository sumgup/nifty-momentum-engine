import click
from momentum_engine.engine import LiveMomentumEngine
from momentum_engine.research.backtester import Backtester
from momentum_engine.research.backtester import Backtester
from momentum_engine.research.performance import PerformanceAnalyzer
from momentum_engine.research.snapshot import SnapshotAnalyzer
from datetime import datetime
from pathlib import Path


UNIVERSE_SHORTCUTS = {
    "nifty100": "data/nifty100_constituents.csv",
    "niftynext50": "data/ind_niftynext50list.csv",
}

@click.group()
def cli():
    """Momentum Engine CLI"""
    pass


@cli.command()
def version():
    click.echo("Momentum Engine v0.1.0")


@cli.command(name="run-live")
@click.option("--config", "-c", required=True, help="Path to config file.")
def run_live(config):
    engine = LiveMomentumEngine(config)
    weights, decision_path = engine.run()

    click.echo(f"Decision report saved to: {decision_path}")
    click.echo("Selected portfolio:")

    for ticker, weight in weights.items():
        click.echo(f"{ticker} -> {weight}")

@cli.command(name="backtest")
@click.option("--config", "-c", default="config/research.yaml", help="Path to config file.")
@click.option("--universe", "-u", default=None, help="Universe CSV file or shortcut (n100, n200, next50).")
def backtest(config, universe):
    """
    Run a full backtest engine.
    """
    
    if universe in UNIVERSE_SHORTCUTS:
        universe = UNIVERSE_SHORTCUTS[universe]

    bt = Backtester(config, universe_override=universe)
    results = bt.run()

    click.echo("Backtest complete.")
    click.echo(f"Universe: {bt.universe_name}")
    click.echo(f"Universe size: {len(bt.universe)}")

    metrics = PerformanceAnalyzer.compute_metrics(results)

    click.echo("\nPerformance Metrics:")
    for k, v in metrics.items():
        if "Drawdown" in k or "Volatility" in k or "CAGR" in k:
            click.echo(f"{k}: {v * 100:.2f}%")
        else:
            click.echo(f"{k}: {v:.2f}")

@cli.command(name="snapshot")
@click.option("--universe", "-u", required=True, help="Universe shortcut or CSV file.")
def snapshot(universe):

    if universe in UNIVERSE_SHORTCUTS:
        universe = UNIVERSE_SHORTCUTS[universe]

    analyzer = SnapshotAnalyzer(universe)
    df = analyzer.run()

    click.echo(f"Universe: {analyzer.universe_name}")
    click.echo(f"Universe size: {len(df)}\n")

        # Drop rows with missing 12M (optional but recommended)
    df = df.dropna(subset=["12M"])

    # Format for human-readable output
    df_display = df.copy()

    for col in ["1M", "3M", "12M", "36M", "60M"]:
        df_display[col] = (df_display[col] * 100).round(2)

    click.echo(df_display.to_string(index=False))

    output_dir = "output/snapshots"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    ts = datetime.today().strftime("%Y-%m-%d")
    df.to_csv(f"{output_dir}/{ts}_{analyzer.universe_name}.csv", index=False)

    click.echo(f"\nSaved to output/snapshots/")