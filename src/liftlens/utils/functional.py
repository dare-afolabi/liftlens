
from collections.abc import Callable
from functools import partial, reduce
from typing import Any

import numpy as np


def compose(*functions: Callable[..., Any]) -> Callable[..., Any]:
    """Compose functions: f(g(h(x)))"""
    def compose_two(f: Callable[..., Any], g: Callable[..., Any]) -> Callable[..., Any]:
        return lambda x: f(g(x))
    return reduce(compose_two, functions, lambda x: x)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Avoid division by zero."""
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return default


def partial_call(func: Callable[..., Any], **fixed_kwargs: Any) -> Callable[..., Any]:
    """Create partial with fixed kwargs."""
    return partial(func, **fixed_kwargs)


# Utility for safe operations
def safe_mean(arr: np.ndarray) -> float:
    arr = np.asarray(arr)
    if len(arr) == 0:
        return np.nan
    return float(arr.mean())


