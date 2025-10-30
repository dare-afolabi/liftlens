from typing import Any, cast

import pandas as pd
import plotly.graph_objects as go
from loguru import logger


def auto_grid(
    figures: list[dict[str, Any]], titles: list[str] | None = None, cols: int = 2
) -> dict[str, Any]:
    """
    Automatically arrange multiple Plotly figures in a grid.
    """
    if titles is None:
        titles = [f"Figure {i + 1}" for i in range(len(figures))]

    rows = (len(figures) + cols - 1) // cols
    # Create subplot figure so we can reference traces by row/col
    from plotly.subplots import make_subplots

    fig = make_subplots(rows=rows, cols=cols, subplot_titles=titles)

    for i, (fdata, _title) in enumerate(zip(figures, titles, strict=False)):
        subfig = go.Figure(fdata)
        row = i // cols + 1
        col = i % cols + 1
        for trace in subfig.data:
            fig.add_trace(trace, row=row, col=col)

    fig.update_layout(
        grid={"rows": rows, "columns": cols},
        height=400 * rows,
        title_text="A/B Test Results Dashboard",
    )

    logger.debug(f"Auto grid: {len(figures)} figures in {rows}x{cols}")
    return cast(dict[str, Any], fig.to_dict())


def summary_table(results: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Create interactive summary table from inference results.
    """
    df = pd.DataFrame(results)
    if df.empty:
        return {"error": "no results"}

    fig = go.Figure(
        data=[
            go.Table(
                header={
                    "values": df.columns.tolist(),
                    "fill_color": "paleturquoise",
                    "align": "left",
                },
                cells={
                    "values": [df[col] for col in df.columns],
                    "fill_color": "lavender",
                    "align": "left",
                },
            )
        ]
    )

    fig.update_layout(title="Statistical Summary")
    return cast(dict[str, Any], fig.to_dict())
