from fastapi.testclient import TestClient

from liftlens.api.server import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_run_experiment(tmp_path, sample_data_path):
    config = {
        "name": "api_test",
        "data": {"type": "csv", "path": str(sample_data_path)},
        "baseline_col": "baseline",
        "outcome_col": "outcome",
        "group_col": "group",
        "metrics": [{"name": "mean", "type": "primary", "func": "mean_diff"}],
    }

    response = client.post("/run", json=config)
    assert response.status_code == 200
    run_id = response.json()["run_id"]

    # Wait for async completion
    import time

    time.sleep(3)

    result = client.get(f"/results/{run_id}")
    assert result.status_code == 200
    assert "results_json" in result.json()
