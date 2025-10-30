
from liftlens.metrics.monitoring import ks_test, psi


def test_psi(sample_data):
    psi_val = psi(sample_data["baseline"], sample_data["outcome"])
    assert 0 <= psi_val < 0.5  # stable


def test_ks_test(sample_data):
    result = ks_test(
        sample_data[sample_data["group"] == "control"]["outcome"],
        sample_data[sample_data["group"] == "treatment"]["outcome"]
    )
    assert result["p_value"] < 0.05  # distributions differ


