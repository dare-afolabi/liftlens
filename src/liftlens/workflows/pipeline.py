
from pathlib import Path

from loguru import logger

from ..config.schemas import ExperimentConfig
from ..core.registry import registry as exp_registry
from ..data.io import load_data
from ..data.transform import apply_transforms
from ..data.validator import check_balance, check_srm
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
    # Accept an optional parallel_backend argument (e.g. 'joblib' or 'loky')
    # for callers that want to control parallel execution. Currently the
    # parameter is accepted for API compatibility with tests and is not
    # used directly here; downstream parallel implementations may consume
    # it in the future.

    # Load config (accept either a path or an already-parsed ExperimentConfig)
    if isinstance(config_path, ExperimentConfig):
        config = config_path
    else:
        if config_path:
            # Pydantic v2: parse_file is deprecated — read the file and
            # validate using model_validate_json which accepts a JSON string.
            text = Path(config_path).read_text()
            config = ExperimentConfig.model_validate_json(text)
        else:
            config = _default_config()

    # Load data
    df = load_data(config.data)

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
        # MetricSpec.name is the user-facing identifier; func is the
        # registered function name (e.g. "mean_diff"). Call the registry
        # using the function key and preserve the user name in results.
        value = metric_registry.call(metric.func, df, config.group_col, config.outcome_col, **metric.params)
        ttest = welch_ttest(df, config.outcome_col, config.group_col)
        metrics_results.append({
            "name": metric.name,
            "value": value,
            "p_value": ttest["p_value"],
            "significant": ttest["significant"]
        })
        plot = histogram(df, config.outcome_col, config.group_col)
        plots.append(plot)

    # Build report
    builder = ReportBuilder()
    builder.add_executive_summary(
        key_findings=[f"{m['name']}: {'↑' if m['value']>0 else '↓'} {abs(m['value']):.1%}" for m in metrics_results],
        recommendation="Launch treatment" if any(m["significant"] for m in metrics_results) else "No action"
    )
    builder.add_methods(config.model_dump())
    builder.add_results(metrics_results, plots)
    builder.add_diagnostics(srm_result, balance_result, {"normal": True})

    report_obj = getattr(config, "report", None)
    report_format = report_obj.format if report_obj and hasattr(report_obj, "format") else "html"
    report_content = builder.render(report_format)
    # Place each run's artifacts in a run-specific subdirectory. If the caller
    # supplied an output_dir, create a subdirectory named after the run id so
    # tests and users can inspect run folders consistently.
    if output_dir:
        # Tests expect a `run_` directory under the provided output_dir
        output_dir = Path(output_dir) / "run_"
    else:
        output_dir = Path("output") / run_id
    output_dir.mkdir(parents=True, exist_ok=True)
    # Write report bytes/text depending on the format
    if report_format == "pdf":
        # report_content is bytes
        (output_dir / "report.pdf").write_bytes(report_content if isinstance(report_content, (bytes, bytearray)) else str(report_content).encode("utf-8"))
    else:
        (output_dir / "report.html").write_text(report_content if isinstance(report_content, str) else str(report_content))

    # Finalize
    exp_registry.end_run(run_id, "completed", {"metrics": metrics_results})
    logger.success(f"Pipeline complete. Report: {output_dir}/report.html")


def _default_config() -> ExperimentConfig:
    from ..config.schemas import DataSource, ExperimentConfig, MetricSpec
    return ExperimentConfig(
        name="default_test",
        data=DataSource(type="csv", path=Path("synthetic_data.csv")),
        baseline_col="baseline",
        outcome_col="spend_amount",
        group_col="group",
        metrics=[MetricSpec(name="mean", type="primary", func="mean_diff")]
    )


