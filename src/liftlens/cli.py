
from pathlib import Path

import typer
from loguru import logger

from .api.server import app as fastapi_app
from .workflows.pipeline import run_pipeline

app = typer.Typer(
    name="liftlens",
    help="An Enterprise-grade A/B Testing Framework CLI",
    add_completion=False
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
    # Accept either a positional config argument or the --config option.
    cfg = config or config_arg
    run_pipeline(config_path=cfg, input_path=input_path, output_dir=output_dir)
    # Provide an explicit stdout message for CLI integration tests that
    # expect progress/result information on stdout.
    print("Pipeline complete")


@app.command()
def serve() -> None:
    """Start the FastAPI server."""
    import uvicorn
    logger.info("Starting FastAPI server on http://0.0.0.0:8000")
    # Intentionally bind to all interfaces for local development/CLI usage.
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="info")  # noqa: S104


@app.command()
def dashboard() -> None:
    """Launch the Streamlit dashboard."""
    import subprocess
    import sys
    logger.info("Launching Streamlit dashboard on http://0.0.0.0:8501")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "liftlens/api/dashboard.py", "--server.port=8501"])  # noqa: S603


if __name__ == "__main__":
    app()


