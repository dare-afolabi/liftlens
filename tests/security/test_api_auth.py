
from fastapi.testclient import TestClient

from liftlens.api.server import app

client = TestClient(app)


def test_api_key_required():
    response = client.post("/run", json={})
    assert response.status_code == 401
    assert "Invalid API Key" in response.json()["detail"]


def test_valid_api_key(monkeypatch):
    monkeypatch.setenv("LIFTLENS_API_KEY", "test-secret")
    # Re-import to reload settings
    import importlib

    import liftlens.config.settings
    importlib.reload(liftlens.config.settings)

    headers = {"X-API-Key": "test-secret"}
    response = client.post("/run", json={}, headers=headers)
    assert response.status_code == 422  # missing body, but auth passed


