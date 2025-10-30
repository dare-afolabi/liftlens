
from typing import Any

import numpy as np
import pandas as pd
from loguru import logger
from scipy import stats

from ..metrics.registry import registry as metric_registry


def welch_ttest(
    df: pd.DataFrame,
    metric_col: str,
    group_col: str = "group"
) -> dict[str, Any]:
    """
    Welch's t-test for unequal variances.
    Returns full result dictionary.
    """
    control = df[df[group_col] == "control"][metric_col].dropna()
    treatment = df[df[group_col] == "treatment"][metric_col].dropna()

    if len(control) < 2 or len(treatment) < 2:
        logger.warning("Insufficient sample size for t-test")
        return {"error": "n < 2 in one group"}

    t_stat, p_value = stats.ttest_ind(treatment, control, equal_var=False, nan_policy='omit')
    mean_diff = treatment.mean() - control.mean()

    # Degrees of freedom (Welch-Satterthwaite)
    se_control = control.std() / np.sqrt(len(control))
    se_treatment = treatment.std() / np.sqrt(len(treatment))
    se_diff = np.sqrt(se_control**2 + se_treatment**2)
    df_welch = (se_control**2 + se_treatment**2)**2 / (
        (se_control**4 / (len(control) - 1)) + (se_treatment**4 / (len(treatment) - 1))
    )

    # Confidence interval
    t_crit = stats.t.ppf(0.975, df_welch)
    ci = (mean_diff - t_crit * se_diff, mean_diff + t_crit * se_diff)

    result = {
        "method": "Welch's t-test",
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "df": float(df_welch),
        "mean_control": float(control.mean()),
        "mean_treatment": float(treatment.mean()),
        "mean_diff": float(mean_diff),
        "ci_95": [float(ci[0]), float(ci[1])],
        "significant": p_value < 0.05,
        "n_control": len(control),
        "n_treatment": len(treatment)
    }
    logger.info(f"Welch t-test: t={t_stat:.3f}, p={p_value:.3f}, diff={mean_diff:.3f}")
    return result


def bootstrap_ci(
    df: pd.DataFrame,
    metric_col: str,
    group_col: str = "group",
    n_boot: int = 10_000,
    alpha: float = 0.05
) -> dict[str, Any]:
    """
    Percentile bootstrap confidence interval for mean difference.
    """
    control = df[df[group_col] == "control"][metric_col].values
    treatment = df[df[group_col] == "treatment"][metric_col].values

    def boot_diff() -> float:
        c_sample = np.random.choice(control, size=len(control), replace=True)
        t_sample = np.random.choice(treatment, size=len(treatment), replace=True)
        return float(t_sample.mean() - c_sample.mean())

    boot_diffs = np.array([boot_diff() for _ in range(n_boot)])
    ci_lower = np.percentile(boot_diffs, (alpha/2)*100)
    ci_upper = np.percentile(boot_diffs, (1 - alpha/2)*100)

    result = {
        "method": "bootstrap",
        "mean_diff": float(treatment.mean() - control.mean()),
        "ci_95": [float(ci_lower), float(ci_upper)],
        "n_boot": n_boot,
        "significant": (ci_lower > 0) or (ci_upper < 0)
    }
    logger.info(f"Bootstrap: diff={result['mean_diff']:.3f}, CI=[{ci_lower:.3f}, {ci_upper:.3f}]")
    return result


def permutation_test(
    df: pd.DataFrame,
    metric_col: str,
    group_col: str = "group",
    n_perm: int = 5_000
) -> dict[str, Any]:
    """
    Permutation test for difference in means.
    """
    observed = metric_registry.call("mean", df, group_col, metric_col)
    combined = df[metric_col].values
    group_labels = df[group_col].values
    sum(group_labels == "treatment")

    perm_diffs = []
    for _ in range(n_perm):
        np.random.shuffle(group_labels)
        perm_treat = combined[group_labels == "treatment"]
        perm_control = combined[group_labels == "control"]
        perm_diffs.append(perm_treat.mean() - perm_control.mean())

    p_value = (np.abs(perm_diffs) >= np.abs(observed)).mean()

    result = {
        "method": "permutation_test",
        "observed_diff": float(observed),
        "p_value": float(p_value),
        "n_perm": n_perm,
        "significant": p_value < 0.05
    }
    logger.info(f"Permutation test: obs={observed:.3f}, p={p_value:.3f}")
    return result


