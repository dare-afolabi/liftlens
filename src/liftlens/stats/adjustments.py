
from typing import Any

import numpy as np
from loguru import logger
from statsmodels.stats.multitest import multipletests


def bonferroni(p_values: list[float], alpha: float = 0.05) -> dict[str, Any]:
    """Bonferroni correction for FWER."""
    n = len(p_values)
    corrected_alpha = alpha / n
    significant = [p < corrected_alpha for p in p_values]
    result = {
        "method": "Bonferroni",
        "n_tests": n,
        "alpha_original": alpha,
        "alpha_corrected": corrected_alpha,
        "p_values": p_values,
        "significant": significant
    }
    logger.info(f"Bonferroni: {sum(significant)}/{n} significant at α={corrected_alpha:.4f}")
    return result


def holm_bonferroni(p_values: list[float], alpha: float = 0.05) -> dict[str, Any]:
    """Holm-Bonferroni step-down procedure."""
    p_sorted = sorted(p_values)
    n = len(p_sorted)
    significant = []
    for i, p in enumerate(p_sorted):
        if p < alpha / (n - i):
            significant.append(True)
        else:
            significant.append(False)
            break
    else:
        significant = [True] * n

    # Map back to original order
    idx = np.argsort(p_values)
    significant = [significant[i] for i in idx]

    result = {
        "method": "Holm-Bonferroni",
        "n_tests": n,
        "p_values": p_values,
        "significant": significant
    }
    logger.info(f"Holm: {sum(significant)}/{n} significant")
    return result


def benjamini_hochberg(p_values: list[float], fdr: float = 0.05) -> dict[str, Any]:
    """Benjamini-Hochberg for FDR control."""
    reject, _, _, _ = multipletests(p_values, alpha=fdr, method='fdr_bh')
    result = {
        "method": "Benjamini-Hochberg",
        "fdr": fdr,
        "p_values": p_values,
        "significant": reject.tolist()
    }
    logger.info(f"BH-FDR: {sum(reject)}/{len(p_values)} significant at FDR={fdr}")
    return result


def closed_testing(
    p_values: list[float],
    alpha: float = 0.05
) -> dict[str, Any]:
    """Closed testing procedure (for strong FWER control)."""
    n = len(p_values)
    p_sorted_idx = np.argsort(p_values)
    significant = [False] * n

    for k in range(1, n + 1):
        subset_p = [p_values[i] for i in p_sorted_idx[:k]]
        # Test intersection hypothesis
        max_p = max(subset_p)
        if max_p <= alpha / k:
            for i in p_sorted_idx[:k]:
                significant[i] = True

    result = {
        "method": "Closed Testing",
        "n_tests": n,
        "p_values": p_values,
        "significant": significant
    }
    logger.info(f"Closed testing: {sum(significant)}/{n} significant")
    return result


