from __future__ import annotations

from pathlib import Path

from loguru import logger

from ..config.schemas import ExperimentConfig
from ..core.registry import registry as exp_registry
from ..data.io import load_data
from ..data.transform import apply_transforms
from ..data.validator import check_balance, check_srm
from ..metrics import ensure_metrics_registered
from ..metrics.registry import registry as metric_registry
from ..report.builder import ReportBuilder
from ..stats.inference import welch_ttest
from ..viz.distributions import histogram


def run_pipeline(
    config_path: Path | ExperimentConfig | None = None,
    input_path: Path | None = None,
    output_dir: Path | None = None,
    parallel_backend: str | None = None,
) -> None:
    """Orchestrate full A/B test pipeline."""
    logger.info("Starting A/B test pipeline")

    ensure_metrics_registered()

    # Load config
    if isinstance(config_path, ExperimentConfig):
        config = config_path
    else:
        if config_path:
            text = Path(config_path).read_text()
            config = ExperimentConfig.model_validate_json(text)
        else:
            config = _default_config()

    # Load data
    df = load_data(config.data)

    # allow input_path override
    if input_path is not None:
        # if user explicitly provides data path, override config.data.path
        df = load_data(config.data.model_copy(update={"path": Path(input_path)}))

    # Validate
    srm_result = check_srm(df, config.group_col)
    balance_result = check_balance(df, config.baseline_col, config.group_col)

    # Transform
    df = apply_transforms(df, config, config.baseline_col, config.outcome_col)

    # Register run
    run_id = exp_registry.start_run(config.name, config.model_dump())

    # Analyze
    metrics_results = []
    plots = []
    for metric in config.metrics:
        value = metric_registry.call(
            metric.func, df, config.group_col, config.outcome_col, **metric.params
        )
        ttest = welch_ttest(df, config.outcome_col, config.group_col)
        metrics_results.append(
            {
                "name": metric.name,
                "value": value,
                "p_value": ttest["p_value"],
                "significant": ttest["significant"],
            }
        )
        plot = histogram(df, config.outcome_col, config.group_col)
        plots.append(plot)

    # Build report
    builder = ReportBuilder()
    builder.add_executive_summary(
        key_findings=[
            f"{m['name']}: {'↑' if m['value'] > 0 else '↓'} {abs(m['value']):.1%}"
            for m in metrics_results
        ],
        recommendation="Launch treatment"
        if any(m["significant"] for m in metrics_results)
        else "No action",
    )
    builder.add_methods(config.model_dump())
    builder.add_results(metrics_results, plots)
    builder.add_diagnostics(srm_result, balance_result, {"normal": True})

    report_obj = getattr(config, "report", None)
    report_format = (
        report_obj.format if report_obj and hasattr(report_obj, "format") else "html"
    )
    report_content = builder.render(report_format)

    # ensure consistent output_dir naming and avoid overwriting
    if output_dir:
        output_dir = Path(output_dir) / f"run_{run_id}"
    else:
        output_dir = Path("output") / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write report
    if report_format == "pdf":
        (output_dir / "report.pdf").write_bytes(
            report_content
            if isinstance(report_content, (bytes, bytearray))
            else str(report_content).encode("utf-8")
        )
    else:
        (output_dir / "report.html").write_text(
            report_content if isinstance(report_content, str) else str(report_content)
        )

    # log both format and path
    exp_registry.end_run(run_id, "completed", {"metrics": metrics_results})
    logger.success(
        f"Pipeline complete. Report: {output_dir}/report.{report_format}"
    )


def _default_config() -> ExperimentConfig:
    from ..config.schemas import DataSource, ExperimentConfig, MetricSpec

    return ExperimentConfig(
        name="default_test",
        data=DataSource(type="csv", path=Path("synthetic_data.csv")),
        baseline_col="baseline",
        outcome_col="spend_amount",
        group_col="group",
        metrics=[MetricSpec(name="mean", type="primary", func="mean_diff")],
    )
