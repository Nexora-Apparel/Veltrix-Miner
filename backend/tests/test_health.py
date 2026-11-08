from fastapi.testclient import TestClient

from app.api.v1 import health
from app.core.config import get_settings
from app.main import app

client = TestClient(app)


def test_liveness_does_not_depend_on_database() -> None:
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_readiness_reports_database_not_configured(monkeypatch) -> None:
    monkeypatch.setattr(get_settings(), "database_url", None)
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.json()["detail"]["database"] == "not_configured"


def test_readiness_reports_connected_database(monkeypatch) -> None:
    monkeypatch.setattr(get_settings(), "database_url", "postgresql://test")
    monkeypatch.setattr(health, "check_database_connection", lambda: True)
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json()["database"] == "connected"


def test_readiness_reports_unavailable_database(monkeypatch) -> None:
    monkeypatch.setattr(get_settings(), "database_url", "postgresql://test")
    monkeypatch.setattr(health, "check_database_connection", lambda: False)
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.json()["detail"]["database"] == "unavailable"
