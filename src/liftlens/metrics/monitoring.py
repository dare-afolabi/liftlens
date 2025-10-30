from typing import Any

import numpy as np
import pandas as pd
from loguru import logger
from scipy import stats


def psi(expected: pd.Series, actual: pd.Series, buckets: int = 10) -> float:
    """
    Population Stability Index (PSI)
    Measures distribution shift between baseline and outcome periods.
    """
    # Create bins based on the expected distribution percentiles and apply to both series
    percentiles = np.linspace(0, 100, buckets + 1)
    bins = np.percentile(expected, percentiles)
    exp_bins = pd.cut(expected, bins, include_lowest=True, duplicates="drop")
    act_bins = pd.cut(actual, bins, include_lowest=True, duplicates="drop")

    exp_pct = pd.Series(exp_bins).value_counts(normalize=True, sort=False)
    act_pct = pd.Series(act_bins).value_counts(normalize=True, sort=False)

    # Align indices
    all_bins = exp_pct.index.union(act_pct.index)
    exp_pct = exp_pct.reindex(all_bins, fill_value=0.0001)
    act_pct = act_pct.reindex(all_bins, fill_value=0.0001)

    psi_value = np.sum((exp_pct - act_pct) * np.log(exp_pct / act_pct))
    logger.debug(f"PSI: {psi_value:.4f}")
    return float(psi_value)


def ks_test(control: pd.Series, treatment: pd.Series) -> dict[str, Any]:
    """Kolmogorov-Smirnov test for distribution difference."""
    ks_stat, p_value = stats.ks_2samp(control, treatment)
    result = {
        "ks_statistic": float(ks_stat),
        "p_value": float(p_value),
        "significant": p_value < 0.05,
    }
    logger.debug(f"KS test: stat={ks_stat:.3f}, p={p_value:.3f}")
    return result


def cvm_test(control: pd.Series, treatment: pd.Series) -> dict[str, Any]:
    """Cramér-von Mises test."""
    # SciPy added cramervonmises_2samp in newer releases; check availability
    try:
        from scipy import stats as _stats
    except ImportError:  # pragma: no cover - extremely unlikely
        logger.warning("scipy not available for CvM test")
        return {"error": "scipy required"}

    if not hasattr(_stats, "cramervonmises_2samp"):
        logger.warning("cramervonmises_2samp not available in installed scipy")
        return {"error": "cramervonmises_2samp not available"}

    result = _stats.cramervonmises_2samp(control, treatment)
    return {
        "cvm_statistic": float(result.statistic),
        "p_value": float(result.pvalue),
        "significant": result.pvalue < 0.05,
    }
