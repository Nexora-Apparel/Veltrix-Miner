from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from app.core.config import get_settings
from app.schemas.market import MarketQuote

SUPPORTED_ASSETS = {
    "btc": "bitcoin",
    "xmr": "monero",
    "ltc": "litecoin",
    "doge": "dogecoin",
}


class MarketDataUnavailable(Exception):
    """Raised when the upstream market provider cannot supply valid data."""


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    if not parsed.is_finite():
        return None
    return parsed


async def fetch_market_quotes(assets: list[str]) -> list[MarketQuote]:
    settings = get_settings()
    requested = [asset.lower().strip() for asset in assets]
    if not requested or any(asset not in SUPPORTED_ASSETS for asset in requested):
        raise ValueError("Unsupported asset requested")

    asset_ids = [SUPPORTED_ASSETS[asset] for asset in requested]
    headers: dict[str, str] = {}
    if settings.coingecko_api_key:
        headers["x-cg-demo-api-key"] = settings.coingecko_api_key

    params = {
        "ids": ",".join(asset_ids),
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true",
    }
    try:
        async with httpx.AsyncClient(
            base_url=settings.coingecko_base_url,
            timeout=httpx.Timeout(6.0, connect=3.0),
            headers=headers,
        ) as client:
            response = await client.get("/api/v3/simple/price", params=params)
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise MarketDataUnavailable("Market provider unavailable") from exc

    if not isinstance(payload, dict):
        raise MarketDataUnavailable("Invalid market provider response")

    retrieved_at = datetime.now(timezone.utc)
    quotes: list[MarketQuote] = []
    for ticker, asset_id in zip(requested, asset_ids, strict=True):
        row = payload.get(asset_id)
        if not isinstance(row, dict):
            raise MarketDataUnavailable(f"Missing quote for {ticker}")
        price = _decimal(row.get("usd"))
        if price is None or price <= 0:
            raise MarketDataUnavailable(f"Invalid quote for {ticker}")
        quotes.append(
            MarketQuote(
                asset_id=ticker,
                price=price,
                market_cap=_decimal(row.get("usd_market_cap")),
                volume_24h=_decimal(row.get("usd_24h_vol")),
                change_24h_pct=_decimal(row.get("usd_24h_change")),
                source="coingecko",
                retrieved_at=retrieved_at,
            )
        )
    return quotes
