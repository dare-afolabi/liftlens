"""Stress test with 1 M rows – verifies dynamic run directory."""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from liftlens.config.schemas import DataSource, ExperimentConfig, MetricSpec
from liftlens.data.io import save_data
from liftlens.workflows.pipeline import run_pipeline


@pytest.mark.slow
def test_pipeline_with_1M_rows(tmp_path: Path) -> None:
    """Stress test with 1 million users."""
    n = 1_000_000
    rng = np.random.default_rng(42)
    control = rng.normal(100, 15, n // 2)
    treatment = rng.normal(108, 15, n // 2)

    df = pd.DataFrame(
        {
            "user_id": [f"user_{i:08d}" for i in range(n)],
            "group": ["control"] * (n // 2) + ["treatment"] * (n // 2),
            "baseline": np.concatenate([control, control]),
            "outcome": np.concatenate([control, treatment]),
        }
    )

    data_path = tmp_path / "large_data.parquet"
    save_data(df, data_path)

    config = ExperimentConfig(
        name="stress_1M",
        data=DataSource(type="parquet", path=str(data_path)),
        baseline_col="baseline",
        outcome_col="outcome",
        group_col="group",
        metrics=[MetricSpec(name="mean", type="primary", func="mean_diff")],
    )

    config_path = tmp_path / "config.json"
    config_path.write_text(config.json())

    start = time.time()
    run_pipeline(config_path, output_dir=tmp_path)
    elapsed = time.time() - start

    # ---------- NEW: dynamic run directory ----------
    run_dirs = list(tmp_path.glob("run_*"))
    assert len(run_dirs) == 1, f"Expected exactly one run directory, got {run_dirs}"
    report_path = run_dirs[0] / "report.html"
    assert report_path.exists(), f"Report missing at {report_path}"
    # -------------------------------------------------

    assert elapsed < 60  # under 1 minute
