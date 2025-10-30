from liftlens.config.schemas import DataSource, ExperimentConfig, MetricSpec
from liftlens.workflows.pipeline import run_pipeline


def test_pipeline_end_to_end(tmp_path, sample_data_path):
    config = ExperimentConfig(
        name="e2e_test",
        data=DataSource(type="csv", path=str(sample_data_path)),
        baseline_col="baseline",
        outcome_col="outcome",
        group_col="group",
        metrics=[MetricSpec(name="mean", type="primary", func="mean_diff")],
    )

    config_path = tmp_path / "config.json"
    config_path.write_text(config.json())

    run_pipeline(config_path, output_dir=tmp_path)

    report_path = tmp_path / "run_" / "report.html"
    assert report_path.exists()
    html = report_path.read_text()
    assert "8." in html or "7." in html  # effect size
