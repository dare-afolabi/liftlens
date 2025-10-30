"""Metrics package: register built-in metrics into the global registry.

This module imports metric implementations and registers them with the
central `MetricRegistry` instance so they are available via simple names
like ``mean`` used in configuration and tests.
"""

from .monitoring import cvm_test, ks_test, psi
from .primary import conversion_rate, mean_diff, sum_metric
from .registry import registry
from .robust import huber_mean, mad, trimmed_mean

# Primary metrics
registry.register("mean_diff", mean_diff, alias="mean")
registry.register("conversion_rate", conversion_rate, alias="cr")
registry.register("sum", sum_metric)

# Robust metrics
registry.register("trimmed_mean", trimmed_mean)
registry.register("huber_mean", huber_mean)
registry.register("mad", mad)

# Monitoring / diagnostics
registry.register("psi", psi)
registry.register("ks_test", ks_test)
registry.register("cvm_test", cvm_test)
