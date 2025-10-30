
from typing import Any

import numpy as np
import pandas as pd
from loguru import logger
from scipy import stats


def normality_test(series: pd.Series, method: str = "shapiro") -> dict[str, Any]:
    """Shapiro-Wilk or Anderson-Darling normality test."""
    if len(series) < 3:
        return {"error": "n < 3"}
    if method == "shapiro":
        stat, p = stats.shapiro(series)
    elif method == "anderson":
        result = stats.anderson(series)
        stat = result.statistic
        p = result.significance_level[2]  # approximate
    else:
        raise ValueError("method must be 'shapiro' or 'anderson'")

    result = {
        "method": method,
        "statistic": float(stat),
        "p_value": float(p) if 'p' in locals() else None,
        "normal": p > 0.05 if 'p' in locals() else stat < result.critical_values[2]
    }
    logger.debug(f"Normality ({method}): stat={stat:.3f}, p={p:.3f}")
    return result


def variance_test(df: pd.DataFrame, metric_col: str, group_col: str = "group") -> dict[str, Any]:
    """Levene's test for equality of variances."""
    control = df[df[group_col] == "control"][metric_col]
    treatment = df[df[group_col] == "treatment"][metric_col]
    stat, p = stats.levene(control, treatment)
    result = {
        "method": "Levene",
        "statistic": float(stat),
        "p_value": float(p),
        "equal_variance": p > 0.05
    }
    logger.debug(f"Levene: stat={stat:.3f}, p={p:.3f}")
    return result


def qq_plot_data(series: pd.Series, n_points: int = 100) -> dict[str, Any]:
    """Return theoretical vs sample quantiles for QQ plot."""
    if len(series) == 0:
        return {"error": "empty series"}
    probs = np.linspace(0.01, 0.99, n_points)
    theoretical = stats.norm.ppf(probs)
    sample = np.percentile(series, probs * 100)
    return {
        "theoretical": theoretical.tolist(),
        "sample": sample.tolist()
    }


def parallel_trends_test(
    df_pre: pd.DataFrame,
    df_post: pd.DataFrame,
    group_col: str,
    metric_col: str
) -> dict[str, Any]:
    """Test for parallel trends assumption in DiD."""
    # Simple slope comparison
    pre_control = df_pre[df_pre[group_col] == "control"][metric_col]
    pre_treatment = df_pre[df_pre[group_col] == "treatment"][metric_col]
    post_control = df_post[df_post[group_col] == "control"][metric_col]
    post_treatment = df_post[df_post[group_col] == "treatment"][metric_col]

    slope_control = post_control.mean() - pre_control.mean()
    slope_treatment = post_treatment.mean() - pre_treatment.mean()
    diff_in_slopes = slope_treatment - slope_control

    result = {
        "slope_control": float(slope_control),
        "slope_treatment": float(slope_treatment),
        "diff_in_slopes": float(diff_in_slopes),
        "parallel": abs(diff_in_slopes) < 0.01 * pre_control.mean()
    }
    logger.info(f"Parallel trends: Δcontrol={slope_control:.3f}, Δtreatment={slope_treatment:.3f}")
    return result


