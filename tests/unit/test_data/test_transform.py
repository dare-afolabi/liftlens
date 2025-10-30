
from liftlens.data.transform import apply_cuped, winsorize


def test_winsorize(sample_data):
    series = sample_data["outcome"]
    win = winsorize(series, (0.05, 0.05))
    assert win.min() >= series.quantile(0.05)
    assert win.max() <= series.quantile(0.95)


def test_apply_cuped(sample_data):
    df = apply_cuped(sample_data.copy(), "outcome", "baseline")
    assert "outcome_cuped" in df.columns
    var_orig = sample_data["outcome"].var()
    var_cuped = df["outcome_cuped"].var()
    assert var_cuped < var_orig


