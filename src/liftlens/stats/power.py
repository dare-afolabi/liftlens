

from collections.abc import Callable
from typing import Any

import numpy as np
from loguru import logger
from scipy import stats

from .inference import welch_ttest


def analytical_power(
    effect_size: float,
    n_control: int,
    n_treatment: int | None = None,
    alpha: float = 0.05,
    two_tailed: bool = True
) -> float:
    """
    Analytical power for two-sample t-test (equal variance assumption).
    """
    n_treatment = n_treatment or n_control
    df = n_control + n_treatment - 2
    ncp = effect_size * np.sqrt((n_control * n_treatment) / (n_control + n_treatment))
    crit = stats.t.ppf(1 - alpha / (1 if not two_tailed else 2), df)
    power = 1 - stats.nct.cdf(crit, df, ncp)
    logger.debug(f"Analytical power: {power:.3f} (d={effect_size}, n1={n_control}, n2={n_treatment})")
    return float(power)


def sample_size_for_power(
    effect_size: float,
    power: float = 0.8,
    alpha: float = 0.05,
    ratio: float = 1.0
) -> int:
    """
    Minimum sample size per group for desired power.
    """
    from scipy.optimize import root_scalar

    def power_diff(n: float) -> float:
        return analytical_power(effect_size, int(n), int(n * ratio), alpha) - power

    result = root_scalar(power_diff, bracket=[10, 1_000_000])
    n = int(np.ceil(result.root))
    logger.info(f"Required n={n} per control group for power={power}, d={effect_size}")
    return n


def simulation_power(
    generate_data: Callable[[int, float], Any],
    effect_size: float,
    n_per_group: int,
    n_sim: int = 1000,
    alpha: float = 0.05
) -> float:
    """Monte Carlo power estimation."""
    significant = 0
    for _ in range(n_sim):
        df = generate_data(n_per_group, effect_size)
        result = welch_ttest(df, "outcome", "group")
        if result.get("significant", False):
            significant += 1
    power = significant / n_sim
    logger.info(f"Simulation power: {power:.3f} ({n_sim} sims, n={n_per_group})")
    return float(power)


