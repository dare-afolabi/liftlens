from liftlens.viz.distributions import histogram


def test_histogram(sample_data):
    plot_data = histogram(sample_data, "outcome")
    assert isinstance(plot_data, dict)
    assert "data" in plot_data
    assert len(plot_data["data"]) == 2  # control + treatment
