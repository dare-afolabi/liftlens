
from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.robust.scale as sm_robust
from loguru import logger


def trimmed_mean(df: pd.DataFrame, group_col: str, metric_col: str, trim: float = 0.1) -> float:
    """
    Trimmed mean difference: mean(treatment, trimmed) - mean(control, trimmed)
    trim: proportion to trim from each tail (0.1 = 10%)
    """
    def _trimmed(s: pd.Series) -> float:
        if len(s) == 0:
            return np.nan
        return float(stats.trim_mean(s, proportiontocut=trim))

    control = df[df[group_col] == "control"][metric_col]
    treatment = df[df[group_col] == "treatment"][metric_col]
    control_trim = _trimmed(control)
    treatment_trim = _trimmed(treatment)
    diff = treatment_trim - control_trim
    logger.debug(f"Trimmed mean diff (trim={trim}): {diff:.6f}")
    return float(diff)


def huber_mean(df: pd.DataFrame, group_col: str, metric_col: str, c: float = 1.345) -> float:
    """
    Huber M-estimator mean difference (robust to outliers)
    c: tuning constant (1.345 ≈ 95% efficiency under normality)
    """
    def _huber(s: pd.Series) -> float:
        if len(s) == 0:
            return np.nan
        # Use statsmodels' Huber class to compute robust location (returns (loc, scale))
        loc, _scale = sm_robust.Huber(c=c)(s.to_numpy())
        return float(loc)

    control = df[df[group_col] == "control"][metric_col]
    treatment = df[df[group_col] == "treatment"][metric_col]
    diff = _huber(treatment) - _huber(control)
    logger.debug(f"Huber mean diff (c={c}): {diff:.6f}")
    return float(diff)


def mad(df: pd.DataFrame, group_col: str, metric_col: str) -> float:
    """
    Median Absolute Deviation (MAD) ratio: MAD(treatment) / MAD(control)
    Returns relative dispersion
    """
    def _mad(s: pd.Series) -> float:
        if len(s) == 0:
            return np.nan
        median = s.median()
        return float((s - median).abs().median())

    control = df[df[group_col] == "control"][metric_col]
    treatment = df[df[group_col] == "treatment"][metric_col]
    mad_control = _mad(control)
    mad_treatment = _mad(treatment)
    ratio = mad_treatment / mad_control if mad_control > 0 else np.inf
    logger.debug(f"MAD ratio: {ratio:.3f}")
    return float(ratio)


# Factory for parameterized trimmed mean
def make_trimmed_mean(trim: float) -> Callable[..., float]:
    def metric(df: pd.DataFrame, group_col: str, metric_col: str, **kwargs: Any) -> float:
        return trimmed_mean(df, group_col, metric_col, trim=trim)
    metric.__name__ = f"trimmed_mean_{int(trim*100)}pct"
    metric.__doc__ = f"Trimmed mean difference (trim {trim*100:.0f}% from each tail)"
    return metric


