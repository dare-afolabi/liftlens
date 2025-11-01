from __future__ import annotations

import importlib
from typing import Final

from .registry import registry

__all__ = ["registry", "ensure_metrics_registered"]

# Mutable container for Final
_metrics_registered: Final[dict[str, bool]] = {"value": False}


def ensure_metrics_registered() -> None:
    """Register all built-in metrics if not already registered."""
    if _metrics_registered["value"]:  # read from key
        return

    # Lazy imports
    primary = importlib.import_module(".primary", __name__)
    robust = importlib.import_module(".robust", __name__)
    monitoring = importlib.import_module(".monitoring", __name__)

    # Primary
    registry.register("mean_diff", primary.mean_diff, alias="mean")
    registry.register("conversion_rate", primary.conversion_rate, alias="cr")
    registry.register("sum", primary.sum_metric)

    # Robust
    registry.register("trimmed_mean", robust.trimmed_mean)
    registry.register("huber_mean", robust.huber_mean)
    registry.register("mad", robust.mad)

    # Monitoring
    registry.register("psi", monitoring.psi)
    registry.register("ks_test", monitoring.ks_test)
    registry.register("cvm_test", monitoring.cvm_test)

    # Mutate the dict
    _metrics_registered["value"] = True
