
import pandas as pd
import pytest

from liftlens.data.io import _detect_type, load_data, save_data


def test_load_csv(sample_data_path):
    df = load_data(sample_data_path)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1000
    assert "outcome" in df.columns


def test_load_parquet(tmp_path, sample_data):
    path = tmp_path / "data.parquet"
    sample_data.to_parquet(path)
    df = load_data(path)
    assert len(df) == 1000


def test_detect_type():
    assert _detect_type("data.csv") == "csv"
    assert _detect_type("s3://bucket/data.parquet") == "parquet"
    with pytest.raises(ValueError):
        _detect_type("unknown.xyz")


def test_save_csv(tmp_path, sample_data):
    path = tmp_path / "out.csv"
    save_data(sample_data, path)
    assert path.exists()
    df = pd.read_csv(path)
    assert len(df) == 1000


