import json
from pathlib import Path

import pytest

from liftlens.config.schemas import DataSource, ExperimentConfig, MetricSpec
from liftlens.workflows.pipeline import run_pipeline


@pytest.mark.slow
def test_full_pipeline_csv(tmp_path: Path, sample_data_path: Path):
    """
    Full E2E test: CSV input → pipeline → HTML report + registry entry.
    """
    config = ExperimentConfig(
        name="csv_full_test",
        data=DataSource(type="csv", path=str(sample_data_path)),
        baseline_col="baseline",
        outcome_col="outcome",
        group_col="group",
        metrics=[MetricSpec(name="mean_lift", type="primary", func="mean_diff")],
    )

    config_path = tmp_path / "config.json"
    config_path.write_text(config.json(indent=2))

    # Run pipeline
    run_pipeline(config_path, output_dir=tmp_path)

    # Validate output directory
    run_dirs = list(tmp_path.glob("run_*"))
    assert len(run_dirs) == 1
    run_dir = run_dirs[0]

    # Validate HTML report
    report_path = run_dir / "report.html"
    assert report_path.exists()
    assert report_path.stat().st_size > 1000

    # Validate registry entry
    from liftlens.core.registry import registry

    runs = registry.list_runs(name="csv_full_test")
    assert len(runs) == 1
    assert runs[0]["status"] == "completed"
    results = json.loads(runs[0]["results_json"])
    assert "mean_lift" in results["metrics"][0]["name"]
