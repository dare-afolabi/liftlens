"""End-to-end pipeline test – uses the same dynamic run folder logic."""

from __future__ import annotations

from pathlib import Path

from liftlens.config.schemas import DataSource, ExperimentConfig, MetricSpec
from liftlens.workflows.pipeline import run_pipeline


def test_pipeline_end_to_end(tmp_path: Path, sample_data_path: Path) -> None:
    """Full pipeline run with the tiny CSV fixture."""
    config = ExperimentConfig(
        name="e2e_test",
        data=DataSource(type="csv", path=str(sample_data_path)),
        baseline_col="baseline",
        outcome_col="outcome",
        group_col="group",
        metrics=[MetricSpec(name="mean", type="primary", func="mean_diff")],
    )

    config_path = tmp_path / "config.json"
    config_path.write_text(config.json())

    run_pipeline(config_path, output_dir=tmp_path)

    # ---------- NEW: dynamic run directory ----------
    run_dirs = list(tmp_path.glob("run_*"))
    assert len(run_dirs) == 1, f"Expected one run directory, got {run_dirs}"
    report_path = run_dirs[0] / "report.html"
    assert report_path.exists(), f"Report missing at {report_path}"
    # -------------------------------------------------

    html = report_path.read_text()
    assert "8." in html or "7." in html  # effect size ~8
