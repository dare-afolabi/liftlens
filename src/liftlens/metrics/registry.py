from collections.abc import Callable
from functools import partial
from typing import Any

from loguru import logger


class MetricRegistry:
    """
    Dynamic registry for KPI functions.
    Supports registration, retrieval, and parameterized calls.
    """

    def __init__(self) -> None:
        self._metrics: dict[str, Callable[..., Any]] = {}
        self._aliases: dict[str, str] = {}

    def register(
        self, name: str, func: Callable[..., Any], *, alias: str | None = None
    ) -> None:
        """
        Register a metric function.

        Args:
            name: Unique metric name
            func: Callable that takes (df, group_col, metric_col) → float
            alias: Optional shorthand
        """
        if name in self._metrics:
            raise ValueError(f"Metric '{name}' already registered")
        self._metrics[name] = func
        if alias:
            self._aliases[alias] = name
        logger.debug(
            f"Registered metric: {name}" + (f" (alias: {alias})" if alias else "")
        )

    def get(self, name: str) -> Callable[..., Any]:
        """Retrieve metric function by name or alias."""
        if name in self._metrics:
            return self._metrics[name]
        elif name in self._aliases:
            return self._metrics[self._aliases[name]]
        else:
            raise KeyError(
                f"Metric '{name}' not found. Available: {list(self._metrics.keys())}"
            )

    def call(
        self, name: str, df: Any, group_col: str, metric_col: str, **params: Any
    ) -> float:
        """Execute metric with parameters."""
        func = self.get(name)
        if params:
            func = partial(func, **params)
        result = func(df, group_col, metric_col)
        logger.debug(f"Computed {name}: {result:.6f}")
        return float(result)

    def list_metrics(self) -> dict[str, str]:
        """Return mapping of name → docstring."""
        return {
            name: func.__doc__.strip().split("\n")[0]
            if func.__doc__
            else "No description"
            for name, func in self._metrics.items()
        }

    def __contains__(self, name: str) -> bool:
        return name in self._metrics or name in self._aliases


# Global registry instance
registry = MetricRegistry()
