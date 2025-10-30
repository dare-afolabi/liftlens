
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import scipy.stats as stats
from loguru import logger


def histogram(
    df: pd.DataFrame,
    metric_col: str,
    group_col: str = "group",
    bins: int = 50,
    opacity: float = 0.6
) -> dict[str, Any]:
    """Overlaid histogram with KDE."""
    fig = go.Figure()

    for group in ["control", "treatment"]:
        data = df[df[group_col] == group][metric_col]
        fig.add_trace(go.Histogram(
            x=data,
            name=group.capitalize(),
            nbinsx=bins,
            opacity=opacity,
            histnorm='probability density'
        ))

    fig.update_layout(
        barmode='overlay',
        title=f"Distribution of {metric_col}",
        xaxis_title=metric_col,
        yaxis_title="Density",
        legend_title="Group"
    )

    logger.debug("Histogram generated")
    from typing import cast
    return cast(dict[str, Any], fig.to_dict())


def kde_plot(
    df: pd.DataFrame,
    metric_col: str,
    group_col: str = "group",
    bandwidth: float | None = None
) -> dict[str, Any]:
    """Kernel Density Estimate overlay."""
    fig = go.Figure()

    for group in ["control", "treatment"]:
        data = df[df[group_col] == group][metric_col].dropna()
        if len(data) == 0:
            continue
        kde = stats.gaussian_kde(data, bw_method=bandwidth)
        x = np.linspace(data.min(), data.max(), 500)
        y = kde(x)
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines',
            name=group.capitalize(),
            fill='tozeroy' if group == "treatment" else None
        ))

    fig.update_layout(
        title=f"KDE of {metric_col}",
        xaxis_title=metric_col,
        yaxis_title="Density"
    )

    from typing import cast
    return cast(dict[str, Any], fig.to_dict())


def ecdf_plot(
    df: pd.DataFrame,
    metric_col: str,
    group_col: str = "group"
) -> dict[str, Any]:
    """Empirical Cumulative Distribution Function."""
    fig = go.Figure()

    for group in ["control", "treatment"]:
        data = np.sort(df[df[group_col] == group][metric_col])
        y = np.arange(1, len(data) + 1) / len(data)
        fig.add_trace(go.Scatter(
            x=data, y=y,
            mode='lines',
            name=group.capitalize()
        ))

    fig.update_layout(
        title=f"ECDF of {metric_col}",
        xaxis_title=metric_col,
        yaxis_title="Cumulative Probability"
    )

    from typing import cast
    return cast(dict[str, Any], fig.to_dict())


