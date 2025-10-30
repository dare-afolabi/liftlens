
from typing import Any, cast

import numpy as np
import pandas as pd
from loguru import logger
from sklearn.ensemble import RandomForestRegressor


def subgroup_analysis(
    df: pd.DataFrame,
    metric_col: str,
    group_col: str,
    subgroups: list[str]
) -> dict[str, Any]:
    """
    Estimate treatment effect per subgroup.
    """
    results = {}
    for col in subgroups:
        for val in df[col].unique():
            subset = df[df[col] == val]
            if len(subset) < 10:
                continue
            effect = subset[subset[group_col] == "treatment"][metric_col].mean() - \
                     subset[subset[group_col] == "control"][metric_col].mean()
            key = f"{col}={val}"
            results[key] = float(effect)
    logger.info(f"Subgroup analysis: {len(results)} subgroups")
    return results


def causal_forest_effect(
    df: pd.DataFrame,
    treatment_col: str,
    outcome_col: str,
    feature_cols: list[str]
) -> np.ndarray:
    """
    Estimate heterogeneous treatment effects using Causal Forest.
    Returns CATE for each observation.
    """
    try:
        from econml.grf import CausalForest
    except ImportError:
        logger.error("econml not installed. Install with: pip install econml")
        return np.array([])

    X = df[feature_cols].values
    T = df[treatment_col].astype(int).values
    Y = df[outcome_col].values

    cf = CausalForest(n_estimators=100, random_state=42)
    cf.fit(Y, T, X=X)
    cate = cf.predict(X).flatten()
    logger.info(f"Causal Forest: CATE estimated for {len(cate)} units")
    return cast(np.ndarray, cate)


def meta_learner_effect(
    df: pd.DataFrame,
    treatment_col: str,
    outcome_col: str,
    feature_cols: list[str],
    learner_type: str = "s-learner"
) -> np.ndarray:
    """
    S-Learner, T-Learner, or X-Learner for HTE.
    """
    try:
        from econml.sklearn_extensions import S_Learner, T_Learner, X_Learner
    except ImportError:
        logger.error("econml not installed")
        return np.array([])

    X = df[feature_cols]
    T = df[treatment_col]
    Y = df[outcome_col]

    if learner_type == "s":
        learner = S_Learner(RandomForestRegressor())
    elif learner_type == "t":
        learner = T_Learner(RandomForestRegressor())
    elif learner_type == "x":
        learner = X_Learner(RandomForestRegressor())
    else:
        raise ValueError("learner_type must be s, t, or x")

    learner.fit(Y, T, X=X)
    cate = learner.effect(X)
    logger.info(f"{learner_type.upper()}-Learner: CATE estimated")
    return cast(np.ndarray, cate)


