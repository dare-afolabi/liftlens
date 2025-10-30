
from typing import Any

import numpy as np
import pandas as pd
from loguru import logger
from pandera import Check, Column, DataFrameSchema
from scipy import stats


def validate_schema(df: pd.DataFrame, source_type: str) -> None:
    """
    Validate DataFrame structure using Pandera.
    Enforces presence of required columns and basic types.
    """
    required_cols = ["user_id", "baseline", "outcome", "group"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    schema: Any = DataFrameSchema({  # type: ignore[no-untyped-call]
        "user_id": Column(str, Check(lambda s: s.nunique() == len(s)), nullable=False),
        "baseline": Column(float, Check(lambda x: x.ge(0).all()), nullable=False),
        "outcome": Column(float, Check(lambda x: x.ge(0).all()), nullable=False),
        "group": Column(str, Check(lambda s: set(s.unique()).issubset({"control", "treatment"}))),
    }, strict=True)

    try:
        schema.validate(df, lazy=True)
        logger.debug("Schema validation passed")
    except Exception as e:
        logger.error(f"Schema validation failed: {e}")
        raise


def check_srm(df: pd.DataFrame, group_col: str = "group", alpha: float = 0.01) -> dict[str, Any]:
    """
    Sample Ratio Mismatch (SRM) detection using chi-squared test.

    Returns:
        dict with p-value, observed/expected counts, and warning flag.
    """
    observed = df[group_col].value_counts().sort_index()
    n = len(df)
    expected = pd.Series([n / 2, n / 2], index=observed.index)

    chi2, p_value = stats.chisquare(observed, expected)
    is_srm = p_value < alpha

    result = {
        "test": "chi-squared",
        "chi2": float(chi2),
        "p_value": float(p_value),
        "observed": observed.to_dict(),
        "expected": expected.to_dict(),
        "is_srm": is_srm,
        "warning": "SRM Detected" if is_srm else None
    }

    if is_srm:
        logger.warning(f"SRM detected: p = {p_value:.2e}")
    else:
        logger.debug(f"SRM check passed: p = {p_value:.3f}")

    return result


def check_balance(
    df: pd.DataFrame,
    baseline_col: str,
    group_col: str = "group",
    alpha: float = 0.05
) -> dict[str, Any]:
    """
    Covariate balance check using standardized mean difference (SMD) and t-test.
    """
    control = df[df[group_col] == "control"][baseline_col]
    treatment = df[df[group_col] == "treatment"][baseline_col]

    smd = _standardized_mean_difference(control, treatment)
    t_stat, p_value = stats.ttest_ind(control, treatment, equal_var=False)

    result = {
        "smd": float(smd),
        "smd_interpretation": _interpret_smd(abs(smd)),
        "t_test_p_value": float(p_value),
        "is_imbalanced": abs(smd) > 0.1 or p_value < alpha
    }

    if result["is_imbalanced"]:
        logger.warning(f"Baseline imbalance: SMD={smd:.3f}, p={p_value:.3f}")
    else:
        logger.debug(f"Balance check passed: SMD={smd:.3f}, p={p_value:.3f}")

    return result


def _standardized_mean_difference(a: pd.Series, b: pd.Series) -> float:
    """Calculate Cohen's d for two groups."""
    diff = a.mean() - b.mean()
    pooled_std = np.sqrt((a.var() + b.var()) / 2)
    return diff / pooled_std if pooled_std > 0 else 0.0


def _interpret_smd(smd: float) -> str:
    if smd < 0.1:
        return "negligible"
    elif smd < 0.2:
        return "small"
    elif smd < 0.5:
        return "medium"
    else:
        return "large"


