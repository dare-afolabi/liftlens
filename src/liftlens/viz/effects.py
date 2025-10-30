from typing import Any, cast

import pandas as pd
import plotly.graph_objects as go
from loguru import logger


def forest_plot(
    effects: list[dict[str, Any]], title: str = "Treatment Effects"
) -> dict[str, Any]:
    """
    Forest plot for multiple metrics or subgroups.
    Each effect dict: {"name", "estimate", "ci_lower", "ci_upper"}
    """
    names = [e["name"] for e in effects]
    estimates = [e["estimate"] for e in effects]
    ci_low = [e["ci_lower"] for e in effects]
    ci_high = [e["ci_upper"] for e in effects]

    fig = go.Figure()

    # Error bars
    fig.add_trace(
        go.Scatter(
            x=ci_low,
            y=names,
            mode="lines",
            line={"color": "black", "width": 1},
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=ci_high,
            y=names,
            mode="lines",
            line={"color": "black", "width": 1},
            showlegend=False,
        )
    )

    # Point estimates
    fig.add_trace(
        go.Scatter(
            x=estimates,
            y=names,
            mode="markers",
            marker={"color": "blue", "size": 8},
            error_x={
                "type": "data",
                "symmetric": False,
                "array": [e["ci_upper"] - e["estimate"] for e in effects],
                "arrayminus": [e["estimate"] - e["ci_lower"] for e in effects],
            },
            name="Effect",
        )
    )

    # Zero line
    fig.add_vline(x=0, line_dash="dash", line_color="gray")

    fig.update_layout(
        title=title, xaxis_title="Effect Size", yaxis={"autorange": "reversed"}
    )

    logger.debug("Forest plot generated")
    return cast(dict[str, Any], fig.to_dict())


def lift_curve(
    df: pd.DataFrame, metric_col: str, group_col: str = "group", n_bins: int = 10
) -> dict[str, Any]:
    """Cumulative lift by percentile."""
    df = df.copy()
    df["percentile"] = pd.qcut(df[metric_col], n_bins, labels=False)
    lift = df.groupby(["percentile", group_col])[metric_col].mean().unstack()
    lift["lift"] = (lift["treatment"] - lift["control"]) / lift["control"]
    lift = lift.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=lift["percentile"], y=lift["lift"], name="Lift"))

    fig.update_layout(
        title=f"Cumulative Lift by {metric_col} Percentile",
        xaxis_title="Percentile",
        yaxis_title="Relative Lift",
    )

    return cast(dict[str, Any], fig.to_dict())
