from pathlib import Path

import pytest

from liftlens.config.schemas import DataSource, ExperimentConfig, MetricSpec
from liftlens.workflows.pipeline import run_pipeline


@pytest.mark.integration
def test_pipeline_postgres(tmp_path: Path, sample_data_path: Path, postgres_url: str):
    """
    E2E test: PostgreSQL input + registry
    """
    # 1. Insert CSV data into PostgreSQL for test
    import pandas as pd
    from sqlalchemy import create_engine

    df = pd.read_csv(sample_data_path)
    engine = create_engine(postgres_url)
    df.to_sql("ab_test_data", engine, if_exists="replace", index=False)

    config = ExperimentConfig(
        name="postgres_test",
        data=DataSource(type="db", path="ab_test_data", connection_url=postgres_url),
        baseline_col="baseline",
        outcome_col="outcome",
        group_col="group",
        metrics=[MetricSpec(name="mean_lift", type="primary", func="mean_diff")],
    )

    config_path = tmp_path / "config.json"
    config_path.write_text(config.json(indent=2))

    # Run pipeline
    run_pipeline(config_path, output_dir=tmp_path)

    # Validate HTML report
    run_dirs = list(tmp_path.glob("run_*"))
    assert len(run_dirs) == 1
    run_dir = run_dirs[0]
    report_path = run_dir / "report.html"
    assert report_path.exists()

    # Validate registry
    from liftlens.core.registry import registry

    runs = registry.list_runs(name="postgres_test")
    assert len(runs) == 1
    assert runs[0]["status"] == "completed"
