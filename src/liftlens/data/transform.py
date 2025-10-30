from typing import Any

import numpy as np
import pandas as pd
from loguru import logger


def winsorize(
    series: pd.Series, limits: tuple[float, float] = (0.01, 0.01)
) -> pd.Series:
    """
    Winsorize a series at given lower and upper quantiles.

    Args:
        series: Input data
        limits: Tuple of (lower_quantile, upper_quantile), e.g., (0.01, 0.01)

    Returns:
        Winsorized series
    """
    if not (0 <= limits[0] <= 0.5 and 0 <= limits[1] <= 0.5):
        raise ValueError("Winsorization limits must be between 0 and 0.5")

    lower, upper = series.quantile([limits[0], 1 - limits[1]])
    winsorized = series.clip(lower, upper)
    # logger调试 is an accidental non-ASCII token; use logger.debug
    logger.debug(
        f"Winsorized at {limits[0] * 100:.1f}th and {(1 - limits[1]) * 100:.1f}th percentiles"
    )
    return winsorized


def apply_cuped(
    df: pd.DataFrame, outcome_col: str, baseline_col: str, group_col: str = "group"
) -> pd.DataFrame:
    """
    Apply CUPED (Controlled-experiment Using Pre-Experiment Data) variance reduction.

    Adds `outcome_cuped` column.
    """
    if baseline_col not in df or outcome_col not in df:
        raise KeyError("Both baseline and outcome columns required for CUPED")

    # Compute covariance adjustment coefficient (theta)
    cov = df[[outcome_col, baseline_col]].cov().iloc[0, 1]
    var_baseline = df[baseline_col].var()
    theta = cov / var_baseline if var_baseline > 0 else 0.0

    baseline_mean = df[baseline_col].mean()
    df["outcome_cuped"] = df[outcome_col] - theta * (df[baseline_col] - baseline_mean)

    # Variance reduction
    var_original = df[outcome_col].var()
    var_cuped = df["outcome_cuped"].var()
    reduction = (1 - var_cuped / var_original) * 100 if var_original > 0 else 0

    logger.info(f"CUPED applied: θ={theta:.4f}, variance reduced by {reduction:.1f}%")
    return df


def log_transform(series: pd.Series, offset: float = 1.0) -> pd.Series:
    """Apply log(x + offset) transformation."""
    if (series < 0).any():
        raise ValueError("Log transform requires non-negative values")
    transformed = np.log(series + offset)
    logger.debug("Log transform applied")
    return transformed


def standardize(series: pd.Series) -> pd.Series:
    """Z-score standardization."""
    mean, std = series.mean(), series.std()
    if std == 0:
        logger.warning("Standard deviation is zero; returning original series")
        return series
    standardized = (series - mean) / std
    logger.debug("Standardization applied")
    return standardized


def apply_transforms(
    df: pd.DataFrame, config: Any, baseline_col: str, outcome_col: str
) -> pd.DataFrame:
    """
    Apply all configured transformations in correct order.
    """
    df = df.copy()

    # Winsorize
    if hasattr(config.transform, "winsorize") and config.transform.winsorize != (0, 0):
        df[f"{baseline_col}_win"] = winsorize(
            df[baseline_col], config.transform.winsorize
        )
        df[f"{outcome_col}_win"] = winsorize(
            df[outcome_col], config.transform.winsorize
        )
        baseline_col = f"{baseline_col}_win"
        outcome_col = f"{outcome_col}_win"
    else:
        df[f"{baseline_col}_win"] = df[baseline_col]
        df[f"{outcome_col}_win"] = df[outcome_col]
        baseline_col = f"{baseline_col}_win"
        outcome_col = f"{outcome_col}_win"

    # CUPED
    if getattr(config.transform, "cuped", False):
        df = apply_cuped(df, outcome_col, baseline_col)
        outcome_col = "outcome_cuped"

    # Log transform
    if getattr(config.transform, "log_transform", False):
        df[outcome_col] = log_transform(df[outcome_col])

    # Standardize
    if getattr(config.transform, "standardize", False):
        df[outcome_col] = standardize(df[outcome_col])

    return df
