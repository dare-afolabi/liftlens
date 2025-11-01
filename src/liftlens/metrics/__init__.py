"""Metrics package: register built-in metrics into the global registry.

This module registers all built-in metrics into the central MetricRegistry
when explicitly imported (e.g. from liftlens.metrics).
It avoids side effects at package import time (e.g. when only running
`liftlens --help`), by registering lazily on first access.
"""

from __future__ import annotations
import importlib

from .registry import registry

__all__ = ["registry", "ensure_metrics_registered"]

_metrics_registered = False


def ensure_metrics_registered() -> None:
    """Register all built-in metrics if not already registered."""
    global _metrics_registered
    if _metrics_registered:
        return

    # Lazy import metric implementations
    primary = importlib.import_module(".primary", __name__)
    robust = importlib.import_module(".robust", __name__)
    monitoring = importlib.import_module(".monitoring", __name__)

    # Primary metrics
    registry.register("mean_diff", primary.mean_diff, alias="mean")
    registry.register("conversion_rate", primary.conversion_rate, alias="cr")
    registry.register("sum", primary.sum_metric)

    # Robust metrics
    registry.register("trimmed_mean", robust.trimmed_mean)
    registry.register("huber_mean", robust.huber_mean)
    registry.register("mad", robust.mad)

    # Monitoring / diagnostics
    registry.register("psi", monitoring.psi)
    registry.register("ks_test", monitoring.ks_test)
    registry.register("cvm_test", monitoring.cvm_test)

    _metrics_registered = True
