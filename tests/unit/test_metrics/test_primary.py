from liftlens.metrics.primary import conversion_rate, mean_diff, ratio_metric


def test_mean_diff(sample_data):
    diff = mean_diff(sample_data, "group", "outcome")
    assert 7.5 < diff < 8.5  # ~8% lift


def test_conversion_rate(sample_data):
    # Add binary column
    df = sample_data.copy()
    df["converted"] = (df["outcome"] > df["outcome"].median()).astype(int)
    cr_diff = conversion_rate(df, "group", "converted")
    assert abs(cr_diff) < 0.1  # should be small


def test_ratio_metric(sample_data):
    df = sample_data.copy()
    df["revenue"] = df["outcome"]
    df["users"] = 1
    ratio = ratio_metric(df, "group", "revenue", "users")
    assert 7.5 < ratio < 8.5
