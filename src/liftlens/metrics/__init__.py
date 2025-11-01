"""Metrics package – lazy registration of all built-in metrics.

The registry is populated **only the first time** the package is touched
(e.g. `from liftlens.metrics import registry` or `ensure_metrics_registered()`).
This avoids side-effects when the CLI is only showing `--help`.
"""

from __future__ import annotations

import importlib
from typing import Final

from .registry import registry

__all__ = ["registry", "ensure_metrics_registered"]

# --------------------------------------------------------------------------- #
# Private flag – guarantees registration happens exactly once per process
# --------------------------------------------------------------------------- #
_metrics_registered: Final[bool] = False   # will be flipped to True after first run


def ensure_metrics_registered() -> None:
    """Register every built-in metric into the global ``registry``."""
    # pylint: disable=global-statement
    global _metrics_registered
    if _metrics_registered:
        return

    # ------------------------------------------------------------------- #
    # 1. Import the implementation modules (this executes their @register)
    # ------------------------------------------------------------------- #
    primary = importlib.import_module(".primary", __name__)
    robust = importlib.import_module(".robust", __name__)
    monitoring = importlib.import_module(".monitoring", __name__)

    # ------------------------------------------------------------------- #
    # 2. Explicitly register the functions that are **not** decorated
    #     (decorators are still executed because the module is imported)
    # ------------------------------------------------------------------- #
    # Primary
    registry.register("mean_diff", primary.mean_diff, alias="mean")
    registry.register("conversion_rate", primary.conversion_rate, alias="cr")
    registry.register("sum", primary.sum_metric)

    # Robust
    registry.register("trimmed_mean", robust.trimmed_mean)
    registry.register("huber_mean", robust.huber_mean)
    registry.register("mad", robust.mad)

    # Monitoring / diagnostics
    registry.register("psi", monitoring.psi)
    registry.register("ks_test", monitoring.ks_test)
    registry.register("cvm_test", monitoring.cvm_test)

    # ------------------------------------------------------------------- #
    # Mark as done – subsequent calls are no-ops
    # ------------------------------------------------------------------- #
    _metrics_registered = True
