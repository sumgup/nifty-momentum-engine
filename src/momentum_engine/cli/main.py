import click
from momentum_engine.engine import LiveMomentumEngine
from momentum_engine.research.backtester import Backtester
from momentum_engine.research.backtester import Backtester
from momentum_engine.research.performance import PerformanceAnalyzer

from datetime import datetime
from pathlib import Path

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
@click.option("--config", "-c", required=True, help="Path to config file.")
def backtest(config):
    """
    Run a full backtest engine.
    """
    bt = Backtester(config)
    results = bt.run()

    click.echo("Backtest complete.")

    # Compute performance metrics
    metrics = PerformanceAnalyzer.compute_metrics(results)

    click.echo("\nPerformance Metrics:")
    for k, v in metrics.items():
        click.echo(f"{k}: {v:.4f}")

    # Save results
    output_dir = bt.config["output"]["directory"]
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    ts = datetime.today().strftime("%Y-%m-%d")
    out_file = f"{output_dir}/{ts}_backtest.csv"
    results.to_csv(out_file, index=False)

    click.echo(f"\nResults saved: {out_file}")