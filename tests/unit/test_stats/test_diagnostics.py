
from liftlens.stats.diagnostics import normality_test, variance_test


def test_normality_test(sample_data):
    result = normality_test(sample_data["outcome"], "shapiro")
    assert result["p_value"] > 0.05  # approx normal


def test_variance_test(sample_data):
    result = variance_test(sample_data, "outcome")
    assert result["equal_variance"]


