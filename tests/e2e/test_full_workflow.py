import json
from pathlib import Path

import pytest

from liftlens.config.schemas import DataSource, ExperimentConfig, MetricSpec
from liftlens.workflows.pipeline import run_pipeline


@pytest.mark.slow
def test_full_e2e(tmp_path: Path, sample_data_path: Path):
    """
    End-to-end test: config → pipeline → report + registry entry.
    """
    # 1. Create valid config
    config = ExperimentConfig(
        name="e2e_full_test",
        data=DataSource(type="csv", path=str(sample_data_path)),
        baseline_col="baseline",
        outcome_col="outcome",
        group_col="group",
        metrics=[MetricSpec(name="mean_lift", type="primary", func="mean_diff")],
    )

    config_path = tmp_path / "config.json"
    config_path.write_text(config.json(indent=2))

    # 2. Run pipeline
    run_pipeline(config_path, output_dir=tmp_path)

    # 3. Validate outputs
    run_dirs = list(tmp_path.glob("run_*"))
    assert len(run_dirs) == 1, "Expected exactly one run directory"
    run_dir = run_dirs[0]

    # Report
    report_path = run_dir / "report.html"
    assert report_path.exists(), "HTML report missing"
    assert report_path.stat().st_size > 1000, "Report too small"

    # Registry entry
    from liftlens.core.registry import registry

    runs = registry.list_runs(name="e2e_full_test")
    assert len(runs) == 1
    assert runs[0]["status"] == "completed"
    results = json.loads(runs[0]["results_json"])
    assert "mean_lift" in results["metrics"][0]["name"]
