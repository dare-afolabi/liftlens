"""liftlens: An Enterprise-grade A/B Testing Framework."""

from __future__ import annotations
import importlib

__version__ = "0.1.0"

__all__ = [
    "cli",
    "config",
    "core",
    "data",
    "metrics",
    "stats",
    "viz",
    "report",
    "workflows",
    "engine",
    "api",
    "utils",
]


def __getattr__(name: str):
    """Lazily import submodules to avoid unintended prints during top-level import."""
    if name in __all__:
        return importlib.import_module(f".{name}", __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
