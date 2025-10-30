from liftlens.data.validator import check_balance, check_srm


def test_check_srm(sample_data):
    result = check_srm(sample_data)
    assert "p_value" in result
    assert not result["is_srm"]  # balanced


def test_check_balance(sample_data):
    result = check_balance(sample_data, "baseline")
    assert abs(result["smd"]) < 0.1
    assert not result["is_imbalanced"]
