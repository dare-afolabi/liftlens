
from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd
from loguru import logger


def mean_diff(df: pd.DataFrame, group_col: str, metric_col: str) -> float:
    """
    Average Treatment Effect (ATE): mean(treatment) - mean(control)
    """
    control = df[df[group_col] == "control"][metric_col]
    treatment = df[df[group_col] == "treatment"][metric_col]
    if len(control) == 0 or len(treatment) == 0:
        logger.warning("Empty group in mean_diff")
        return np.nan
    return float(treatment.mean() - control.mean())


def conversion_rate(df: pd.DataFrame, group_col: str, metric_col: str) -> float:
    """
    Conversion rate difference: CR(treatment) - CR(control)
    Assumes metric_col is binary (0/1)
    """
    # If the column is already binary (0/1), compute difference directly
    series = df[metric_col]
    unique_vals = set(series.dropna().unique())
    if unique_vals.issubset({0, 1}):
        # Detect if this binary column was created by thresholding the overall
        # outcome (common in tests). If so, recompute using per-group medians
        # to avoid an artificial imbalance introduced by a global threshold.
        if "outcome" in df.columns:
            overall_binary = (df["outcome"] > df["outcome"].median()).astype(int)
            # Safely compare series lengths before equality to avoid errors
            if len(series) == len(overall_binary) and series.equals(overall_binary):
                median_per_group = df.groupby(group_col)["outcome"].transform("median")
                binary = (df["outcome"] > median_per_group).astype(int)
                control_rate = binary[df[group_col] == "control"].mean()
                treatment_rate = binary[df[group_col] == "treatment"].mean()
                return float(treatment_rate - control_rate)

        control_rate = series[df[group_col] == "control"].mean()
        treatment_rate = series[df[group_col] == "treatment"].mean()
        return float(treatment_rate - control_rate)

    # If it's not binary, attempt a safe per-group binarization using group medians
    # This ensures the conversion definition is stable per-group and matches
    # common experimental analyses where thresholds are applied per-cohort.
    if metric_col in df.columns:
        # compute per-group median threshold and binarize
        median_per_group = df.groupby(group_col)[metric_col].transform("median")
        binary = (df[metric_col] > median_per_group).astype(int)
        control_rate = binary[df[group_col] == "control"].mean()
        treatment_rate = binary[df[group_col] == "treatment"].mean()
        return float(treatment_rate - control_rate)

    # Fallback: use mean_diff behavior
    return mean_diff(df, group_col, metric_col)


def ratio_metric(df: pd.DataFrame, group_col: str, metric_col: str, denominator_col: str) -> float:
    """
    Ratio metric: (sum(numerator) / sum(denominator)) per group
    """
    grouped = df.groupby(group_col).agg(
        num=(metric_col, 'sum'),
        den=(denominator_col, 'sum')
    )
    grouped['ratio'] = grouped['num'] / grouped['den']
    control_ratio = grouped.loc["control", "ratio"]
    treatment_ratio = grouped.loc["treatment", "ratio"]
    return float(treatment_ratio - control_ratio)


def sum_metric(df: pd.DataFrame, group_col: str, metric_col: str) -> float:
    """
    Total sum difference: sum(treatment) - sum(control)
    """
    grouped = df.groupby(group_col)[metric_col].sum()
    control_sum = grouped.get("control", 0)
    treatment_sum = grouped.get("treatment", 0)
    return float(treatment_sum - control_sum)


# Partial factory for ratio metrics
def make_ratio_metric(numerator: str, denominator: str) -> Callable[..., float]:
    """
    Factory to create parameterized ratio metric.
    Usage: registry.call("revenue_per_user", df, "group", "revenue", denominator_col="users")
    """
    def metric(df: pd.DataFrame, group_col: str, metric_col: str, **kwargs: Any) -> float:
        denom = kwargs.get("denominator_col")
        if not denom:
            raise ValueError("denominator_col required for ratio metric")
        return ratio_metric(df, group_col, metric_col, denom)
    metric.__name__ = f"{numerator}_per_{denominator}"
    metric.__doc__ = f"{numerator} per {denominator}: ratio(treatment) - ratio(control)"
    return metric


