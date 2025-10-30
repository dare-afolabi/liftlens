import pytest

from liftlens.engine.parallel import parallel_apply


def slow_function(x):
    import time

    time.sleep(0.01)
    return x**2


def test_parallel_joblib():
    items = list(range(100))
    results = parallel_apply(slow_function, items, backend="joblib")
    assert results == [i**2 for i in items]


def test_parallel_dask():
    try:
        results = parallel_apply(slow_function, list(range(50)), backend="dask")
        assert len(results) == 50
    except ImportError:
        pytest.skip("dask not installed")


def test_parallel_ray():
    try:
        results = parallel_apply(slow_function, list(range(50)), backend="ray")
        assert len(results) == 50
    except ImportError:
        pytest.skip("ray not installed")
