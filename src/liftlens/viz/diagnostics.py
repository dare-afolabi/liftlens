from typing import Any, cast

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from loguru import logger


def love_plot(
    balance_before: dict[str, float],
    balance_after: dict[str, float],
    threshold: float = 0.1,
) -> dict[str, Any]:
    """
    Love plot for covariate balance (SMD before/after adjustment).
    """
    covariates = sorted(set(balance_before.keys()) & set(balance_after.keys()))

    before = [abs(balance_before[c]) for c in covariates]
    after = [abs(balance_after[c]) for c in covariates]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=before,
            y=covariates,
            mode="markers",
            name="Before",
            marker={"color": "red", "size": 10},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=after,
            y=covariates,
            mode="markers",
            name="After",
            marker={"color": "green", "size": 10},
        )
    )

    # Threshold line
    fig.add_vline(
        x=threshold, line_dash="dash", line_color="gray", annotation_text="0.1"
    )

    fig.update_layout(
        title="Love Plot: Covariate Balance",
        xaxis_title="Absolute Standardized Mean Difference",
        yaxis_title="Covariate",
        legend_title="Adjustment",
    )

    logger.debug("Love plot generated")
    return cast(dict[str, Any], fig.to_dict())


def balance_table(
    df: pd.DataFrame, covariates: list[str], group_col: str = "group"
) -> pd.DataFrame:
    """
    Summary table of means, SDs, and SMD by group.
    """
    results = []
    for cov in covariates:
        control = df[df[group_col] == "control"][cov]
        treatment = df[df[group_col] == "treatment"][cov]

        mean_c = control.mean()
        mean_t = treatment.mean()
        sd_c = control.std()
        sd_t = treatment.std()
        smd = (mean_t - mean_c) / np.sqrt((sd_c**2 + sd_t**2) / 2)

        results.append(
            {
                "covariate": cov,
                "control_mean": mean_c,
                "treatment_mean": mean_t,
                "control_sd": sd_c,
                "treatment_sd": sd_t,
                "smd": smd,
                "balanced": abs(smd) <= 0.1,
            }
        )

    table = pd.DataFrame(results)
    logger.debug(f"Balance table: {len(table)} covariates")
    return table


def residual_plot(model: Any, title: str = "Residuals vs Fitted") -> dict[str, Any]:
    """
    Residual diagnostics for regression models.
    Requires statsmodels model with .resid and .fittedvalues
    """
    try:
        resid = model.resid
        fitted = model.fittedvalues
    except AttributeError:
        logger.error("Model must have .resid and .fittedvalues")
        return {"error": "invalid model"}

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=fitted, y=resid, mode="markers", marker={"opacity": 0.6}, name="Residuals"
        )
    )

    fig.add_hline(y=0, line_dash="dash", line_color="red")

    fig.update_layout(title=title, xaxis_title="Fitted Values", yaxis_title="Residuals")

    return cast(dict[str, Any], fig.to_dict())
