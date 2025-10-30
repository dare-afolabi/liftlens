

import pandas as pd
from loguru import logger


def weighted_index(
    df: pd.DataFrame,
    group_col: str,
    metric_col: str,
    weights: dict[str, float] | None = None,
    submetrics: list[str] | None = None
) -> float:
    """
    Composite index: weighted average of standardized sub-metrics.

    Args:
        submetrics: List of column names to include
        weights: Dict of {metric: weight}, defaults to equal
    """
    if not submetrics:
        raise ValueError("submetrics list required")

    # Standardize each submetric
    standardized = {}
    for col in submetrics:
        if col not in df.columns:
            logger.warning(f"Submetric {col} not in data")
            continue
        series = df[col]
        std = (series - series.mean()) / series.std()
        standardized[col] = std

    sub_df = pd.DataFrame(standardized)
    sub_df[group_col] = df[group_col]

    # Apply weights
    if not weights:
        weights = {col: 1.0 for col in sub_df.columns if col != group_col}
    total_weight = sum(weights.values())
    weights = {k: v / total_weight for k, v in weights.items()}

    # Weighted sum per row
    sub_df["index"] = sum(weights.get(col, 0) * sub_df[col] for col in weights)

    # Mean difference
    diff = sub_df[sub_df[group_col] == "treatment"]["index"].mean() - \
           sub_df[sub_df[group_col] == "control"]["index"].mean()

    logger.debug(f"Weighted index: {diff:.6f} (weights: {weights})")
    return float(diff)


