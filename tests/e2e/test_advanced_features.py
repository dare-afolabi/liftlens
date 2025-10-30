
import json
import subprocess
import sys
from pathlib import Path

import pytest

from liftlens.config.schemas import DataSource, ExperimentConfig, MetricSpec
from liftlens.workflows.pipeline import run_pipeline


@pytest.mark.slow
def test_cuped_sequential_parallel(tmp_path: Path, sample_data_path: Path):
    """
    Test CUPED, sequential testing, and parallel execution.
    """
    config = ExperimentConfig(
        name="advanced_test",
        data=DataSource(type="csv", path=str(sample_data_path)),
        baseline_col="baseline",
        outcome_col="outcome",
        group_col="group",
        metrics=[MetricSpec(name="mean_lift", type="primary", func="mean_diff")],
        transform={"cuped": True},
        stats={"sequential": True, "alpha": 0.05},
    )

    config_path = tmp_path / "config.json"
    config_path.write_text(config.json(indent=2))

    # Run pipeline
    run_pipeline(config_path, output_dir=tmp_path, parallel_backend="joblib")

    run_dirs = list(tmp_path.glob("run_*"))
    assert len(run_dirs) == 1
    report_path = run_dirs[0] / "report.html"
    assert report_path.exists()

@pytest.mark.integration
def test_cli_invocation(tmp_path: Path, sample_data_path: Path):
    """
    Test CLI triggers the pipeline correctly.
    """
    config = {
        "name": "cli_test",
        "data": {"type": "csv", "path": str(sample_data_path)},
        "baseline_col": "baseline",
        "outcome_col": "outcome",
        "group_col": "group",
        "metrics": [{"name": "mean_lift", "type": "primary", "func": "mean_diff"}]
    }
    config_path = tmp_path / "cli_config.json"
    config_path.write_text(json.dumps(config))

    # CLI command
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "liftlens.cli", "run", str(config_path), "--output_dir", str(tmp_path)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    run_dirs = list(tmp_path.glob("run_*"))
    assert len(run_dirs) == 1
    report_path = run_dirs[0] / "report.html"
    assert report_path.exists()

@pytest.mark.integration
def test_pdf_output(tmp_path: Path, sample_data_path: Path):
    """
    Test PDF report generation (requires WeasyPrint dependencies)
    """
    config = ExperimentConfig(
        name="pdf_test",
        data=DataSource(type="csv", path=str(sample_data_path)),
        baseline_col="baseline",
        outcome_col="outcome",
        group_col="group",
        metrics=[MetricSpec(name="mean_lift", type="primary", func="mean_diff")],
        report={"format": "pdf"}
    )

    config_path = tmp_path / "config.json"
    config_path.write_text(config.json(indent=2))

    # Run pipeline
    run_pipeline(config_path, output_dir=tmp_path)

    run_dirs = list(tmp_path.glob("run_*"))
    assert len(run_dirs) == 1
    pdf_path = run_dirs[0] / "report.pdf"
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 1000

