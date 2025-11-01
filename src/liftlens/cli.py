from __future__ import annotations

from pathlib import Path

import typer
import uvicorn
from loguru import logger

from liftlens.api.server import app as fastapi_app

# ------------------------------------------------------------------ #
# Absolute imports – always resolve correctly
# ------------------------------------------------------------------ #
from liftlens.metrics import ensure_metrics_registered
from liftlens.workflows.pipeline import run_pipeline

app = typer.Typer(
    name="liftlens",
    help="An Enterprise-grade A/B Testing Framework CLI",
    add_completion=False,
)


@app.command()
def run(
    config_arg: Path | None = typer.Argument(
        None, help="Path to experiment config (YAML/JSON)"
    ),
    config: Path | None = typer.Option(
        None, "--config", "-c", help="Path to experiment config (YAML/JSON)"
    ),
    input_path: Path | None = typer.Option(
        None, "--input", "-i", help="Input data path (CSV/Parquet)"
    ),
    output_dir: Path | None = typer.Option(
        None, "--output", "--output_dir", "-o", help="Output directory"
    ),
) -> None:
    """Run the full A/B test pipeline."""
    logger.info("Starting A/B test pipeline")

    # ------------------------------------------------------------------ #
    # 1. Ensure all built-in metrics are registered
    # ------------------------------------------------------------------ #
    ensure_metrics_registered()

    # ------------------------------------------------------------------ #
    # 2. Resolve config path (positional or --config)
    # ------------------------------------------------------------------ #
    cfg = config or config_arg
    if cfg is None:
        raise typer.BadParameter("Config path is required (use --config or positional argument)")

    # ------------------------------------------------------------------ #
    # 3. Run pipeline
    # ------------------------------------------------------------------ #
    run_pipeline(config_path=cfg, input_path=input_path, output_dir=output_dir)

    # ------------------------------------------------------------------ #
    # 4. Explicit stdout for test harnesses
    # ------------------------------------------------------------------ #
    print("Pipeline complete")


@app.command()
def serve() -> None:
    """Start the FastAPI server."""
    logger.info("Starting FastAPI server on http://0.0.0.0:8000")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="info")  # noqa: S104


@app.command()
def dashboard() -> None:
    """Launch the Streamlit dashboard."""
    import subprocess
    import sys

    logger.info("Launching Streamlit dashboard on http://0.0.0.0:8501")
    subprocess.run(  # noqa: S603
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "liftlens/api/dashboard.py",
            "--server.port=8501",
        ]
    )


if __name__ == "__main__":
    app()
