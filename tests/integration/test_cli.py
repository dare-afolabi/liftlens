
import subprocess
import sys


def test_cli_run(tmp_path, sample_data_path):
    config = tmp_path / "config.json"
    config.write_text(f"""
    {{
      "name": "cli_test",
      "data": {{"type": "csv", "path": "{sample_data_path}"}},
      "baseline_col": "baseline",
      "outcome_col": "outcome",
      "group_col": "group",
      "metrics": [{{"name": "mean", "type": "primary", "func": "mean_diff"}}]
    }}
    """)

    result = subprocess.run([  # noqa: S603
        sys.executable, "-m", "liftlens.cli", "run",
        "--config", str(config),
        "--output", str(tmp_path)
    ], capture_output=True, text=True)

    assert result.returncode == 0
    assert "Pipeline complete" in result.stdout

    report = list(tmp_path.rglob("report.html"))[0]
    assert report.exists()


