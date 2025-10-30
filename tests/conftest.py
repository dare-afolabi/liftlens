
import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from liftlens.core.session import session
from liftlens.data.io import save_data


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Global test setup: clean temp, set seed."""
    session.seed = 42
    session._set_seeds()
    yield
    session.cleanup()


@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Standard synthetic dataset for unit tests."""
    np.random.seed(42)
    n = 1000
    control = np.random.normal(100, 15, n // 2)
    treatment = np.random.normal(108, 15, n // 2)  # 8% lift
    df = pd.DataFrame({
        "user_id": [f"user_{i}" for i in range(n)],
        "group": ["control"] * (n // 2) + ["treatment"] * (n // 2),
        "baseline": np.concatenate([control, control]),
        "outcome": np.concatenate([control, treatment])
    })
    return df


@pytest.fixture
def sample_data_path(sample_data, tmp_path) -> Path:
    """Save sample data to temp CSV."""
    path = tmp_path / "data.csv"
    save_data(sample_data, path)
    return path


@pytest.fixture
def config_dict():
    return {
        "name": "test_exp",
        "data": {"type": "csv", "path": "data.csv"},
        "baseline_col": "baseline",
        "outcome_col": "outcome",
        "group_col": "group",
        "metrics": [{"name": "mean", "type": "primary", "func": "mean_diff"}]
    }


@pytest.fixture
def postgres_url():
    """Provide a Postgres URL via TEST_POSTGRES_URL env var or skip tests.

    Many CI/dev environments won't have Postgres available. Tests that
    require Postgres should set TEST_POSTGRES_URL in the environment. If
    it's not set, skip Postgres-dependent tests to keep the suite
    runnable in lightweight environments.
    """
    url = os.getenv("TEST_POSTGRES_URL")
    if not url:
        pytest.skip("Postgres not configured - skipping postgres integration tests")
    return url


