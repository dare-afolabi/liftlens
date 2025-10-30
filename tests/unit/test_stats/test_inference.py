
from liftlens.stats.inference import bootstrap_ci, welch_ttest


def test_welch_ttest(sample_data):
    result = welch_ttest(sample_data, "outcome")
    assert result["p_value"] < 0.05
    assert result["significant"]


def test_bootstrap_ci(sample_data):
    result = bootstrap_ci(sample_data, "outcome")
    assert result["ci_95"][0] > 5.0
    assert result["significant"]


