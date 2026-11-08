from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest

from app.core.config import Settings
from app.main import create_app


def preflight(client: TestClient, origin: str):
    return client.options(
        "/api/v1/health/live",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "accept",
        },
    )


def test_cors_allows_only_the_configured_console_origin() -> None:
    client = TestClient(create_app(Settings(web_origin="https://console.example")))
    response = preflight(client, "https://console.example")
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://console.example"
    assert response.headers["access-control-allow-credentials"] == "false"
    assert "https://attacker.example" not in response.headers["access-control-allow-origin"]


def test_cors_rejects_an_unlisted_origin() -> None:
    client = TestClient(create_app(Settings(web_origin="https://console.example")))
    response = preflight(client, "https://attacker.example")
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_cors_is_disabled_when_no_console_origin_is_configured() -> None:
    client = TestClient(create_app(Settings(web_origin=None)))
    response = preflight(client, "https://console.example")
    assert "access-control-allow-origin" not in response.headers


@pytest.mark.parametrize(
    "origin",
    [
        "*",
        "http://console.example",
        "https://console.example/path",
        "https://user:password@console.example",
        "https://console.example?debug=true",
    ],
)
def test_web_origin_rejects_wildcards_insecure_or_non_origin_urls(origin: str) -> None:
    with pytest.raises(ValidationError):
        Settings(web_origin=origin)
