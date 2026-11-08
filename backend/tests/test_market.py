from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from app.api.v1 import market
from app.main import app
from app.schemas.market import MarketQuote
from app.services.market_data import MarketDataUnavailable

client = TestClient(app)


def test_quotes_returns_normalized_provider_data(monkeypatch) -> None:
    async def fake_fetch(assets: list[str]) -> list[MarketQuote]:
        assert assets == ["btc"]
        return [
            MarketQuote(
                asset_id="btc",
                price=Decimal("65000.12"),
                market_cap=Decimal("1000000000000"),
                volume_24h=Decimal("20000000000"),
                change_24h_pct=Decimal("1.25"),
                source="coingecko",
                retrieved_at=datetime.now(timezone.utc),
            )
        ]

    monkeypatch.setattr(market, "fetch_market_quotes", fake_fetch)
    response = client.get("/api/v1/market/quotes?assets=btc")
    assert response.status_code == 200
    quote = response.json()[0]
    assert quote["asset_id"] == "btc"
    assert quote["price"] == "65000.12"
    assert quote["source"] == "coingecko"
    assert quote["retrieved_at"]


def test_quotes_rejects_unsupported_assets() -> None:
    response = client.get("/api/v1/market/quotes?assets=btc,unknown")
    assert response.status_code == 400


def test_quotes_reports_provider_outage(monkeypatch) -> None:
    async def fake_fetch(assets: list[str]) -> list[MarketQuote]:
        raise MarketDataUnavailable("upstream down")

    monkeypatch.setattr(market, "fetch_market_quotes", fake_fetch)
    response = client.get("/api/v1/market/quotes?assets=btc")
    assert response.status_code == 503
    assert response.json()["detail"] == "Market data temporarily unavailable"
