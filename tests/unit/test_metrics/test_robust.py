
from liftlens.metrics.robust import huber_mean, trimmed_mean


def test_trimmed_mean(sample_data):
    trim_diff = trimmed_mean(sample_data, "group", "outcome", trim=0.1)
    assert abs(trim_diff - 8.0) < 1.0


def test_huber_mean(sample_data):
    # Add outliers
    df = sample_data.copy()
    df.loc[df["group"] == "treatment", "outcome"].iloc[:5] *= 10
    huber_diff = huber_mean(df, "group", "outcome")
    assert 7.0 < huber_diff < 9.0


