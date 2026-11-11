from datetime import datetime, timedelta, timezone

import pytest

from app.staging_smoke import (
    SmokeCheckError,
    _NoRedirect,
    normalize_base_url,
    validate_liveness,
    validate_quotes,
    validate_readiness,
)


NOW = datetime(2026, 11, 11, 12, 0, tzinfo=timezone.utc)


def quote(asset: str, *, timestamp: datetime | None = None) -> dict[str, str]:
    retrieved_at = timestamp or NOW
    return {
        "asset_id": asset,
        "currency": "usd",
        "price": "123.45",
        "source": "coingecko",
        "retrieved_at": retrieved_at.isoformat().replace("+00:00", "Z"),
    }


def valid_quotes() -> list[dict[str, str]]:
    return [quote(asset) for asset in ("btc", "xmr", "ltc", "doge")]


def test_normalize_base_url_accepts_https_origin() -> None:
    assert normalize_base_url(" https://miner.example.test ") == "https://miner.example.test/"


@pytest.mark.parametrize(
    "value",
    [
        "http://miner.example.test",
        "https://user:pass@miner.example.test",
        "https://miner.example.test/path",
        "https://miner.example.test?token=x",
        "https://miner.example.test#fragment",
        "",
    ],
)
def test_normalize_base_url_rejects_unsafe_or_ambiguous_urls(value: str) -> None:
    with pytest.raises(SmokeCheckError):
        normalize_base_url(value)


def test_liveness_requires_alive_status() -> None:
    validate_liveness({"status": "alive"})
    with pytest.raises(SmokeCheckError):
        validate_liveness({"status": "degraded"})


def test_readiness_requires_connected_database() -> None:
    validate_readiness({"status": "ready", "database": "connected"})
    with pytest.raises(SmokeCheckError, match="not_configured"):
        validate_readiness({"status": "not_ready", "database": "not_configured"})


def test_quotes_require_exact_asset_coverage_and_valid_provenance() -> None:
    validate_quotes(valid_quotes(), now=NOW)

    duplicate = valid_quotes()
    duplicate[-1] = quote("btc")
    with pytest.raises(SmokeCheckError, match="duplicate"):
        validate_quotes(duplicate, now=NOW)

    wrong_source = valid_quotes()
    wrong_source[0]["source"] = "mock"
    with pytest.raises(SmokeCheckError, match="provenance"):
        validate_quotes(wrong_source, now=NOW)


def test_quotes_reject_non_positive_or_non_finite_prices() -> None:
    invalid = valid_quotes()
    invalid[0]["price"] = "0"
    with pytest.raises(SmokeCheckError, match="positive"):
        validate_quotes(invalid, now=NOW)

    invalid[0]["price"] = "NaN"
    with pytest.raises(SmokeCheckError, match="positive"):
        validate_quotes(invalid, now=NOW)


def test_quotes_reject_stale_and_excessively_future_timestamps() -> None:
    stale = valid_quotes()
    stale[0] = quote("btc", timestamp=NOW - timedelta(minutes=6))
    with pytest.raises(SmokeCheckError, match="older"):
        validate_quotes(stale, now=NOW)

    future = valid_quotes()
    future[0] = quote("btc", timestamp=NOW + timedelta(seconds=61))
    with pytest.raises(SmokeCheckError, match="future"):
        validate_quotes(future, now=NOW)


def test_quotes_require_timezone_aware_timestamps() -> None:
    invalid = valid_quotes()
    invalid[0]["retrieved_at"] = "2026-11-11T12:00:00"
    with pytest.raises(SmokeCheckError, match="timezone"):
        validate_quotes(invalid, now=NOW)



def test_protection_bypass_header_is_not_forwarded_through_redirects() -> None:
    from urllib.request import Request

    handler = _NoRedirect()
    request = Request("https://staging.example.test/api/v1/health/live")
    assert handler.redirect_request(
        request,
        None,
        302,
        "Found",
        {},
        "https://attacker.example.test/collect",
    ) is None
