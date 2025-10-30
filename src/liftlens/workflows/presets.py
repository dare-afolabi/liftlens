
from ..config.schemas import DataSource, ExperimentConfig, MetricSpec, TransformConfig


def revenue_test() -> ExperimentConfig:
    """Preset for revenue per user test."""
    return ExperimentConfig(
        name="Revenue A/B Test",
        data=DataSource(type="csv", path=__import__('pathlib').Path("revenue_data.csv")),
        baseline_col="pre_spend",
        outcome_col="post_spend",
        group_col="variant",
        metrics=[
            MetricSpec(name="revenue_lift", type="primary", func="mean_diff"),
            MetricSpec(name="arpu", type="primary", func="ratio_metric", params={"denominator_col": "active_users"})
        ],
        transform=TransformConfig(winsorize=(0.01, 0.01), cuped=True, log_transform=True)
    )


def engagement_suite() -> ExperimentConfig:
    """Multi-metric engagement test."""
    return ExperimentConfig(
        name="Engagement Suite",
        data=DataSource(type="parquet", path=__import__('pathlib').Path("engagement.parquet")),
        baseline_col="baseline_sessions",
        outcome_col="sessions",
        group_col="group",
        metrics=[
            MetricSpec(name="sessions", type="primary", func="mean_diff"),
            MetricSpec(name="duration", type="primary", func="mean_diff"),
            MetricSpec(name="index", type="composite", func="weighted_index", params={"submetrics": ["sessions", "duration"]})
        ]
    )


