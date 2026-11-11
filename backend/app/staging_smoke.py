"""Fail-closed smoke verification for the protected VELTRIX MINER staging API.

The Vercel automation-bypass credential is read only from the process
environment. It must never be added to Android BuildConfig or an APK.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

EXPECTED_ASSETS = {"btc", "xmr", "ltc", "doge"}
MAX_QUOTE_AGE = timedelta(minutes=5)
MAX_FUTURE_SKEW = timedelta(seconds=60)
REQUEST_TIMEOUT_SECONDS = 15
MAX_RESPONSE_BYTES = 256 * 1024


class SmokeCheckError(RuntimeError):
    """Raised when staging does not satisfy a release smoke-check gate."""


def normalize_base_url(value: str) -> str:
    parsed = urlsplit(value.strip())
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
    ):
        raise SmokeCheckError(
            "VELTRIX_STAGING_BASE_URL must be an HTTPS origin without "
            "credentials, path, query, or fragment"
        )
    return value.strip().rstrip("/") + "/"


def validate_liveness(payload: object) -> None:
    if not isinstance(payload, dict) or payload.get("status") != "alive":
        raise SmokeCheckError("liveness payload is invalid")


def validate_readiness(payload: object) -> None:
    if (
        not isinstance(payload, dict)
        or payload.get("status") != "ready"
        or payload.get("database") != "connected"
    ):
        database = payload.get("database") if isinstance(payload, dict) else None
        raise SmokeCheckError(
            f"readiness gate failed (database={database or 'unknown'})"
        )


def _parse_timestamp(value: object) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise SmokeCheckError("quote retrieval timestamp is missing")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SmokeCheckError("quote retrieval timestamp is invalid") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SmokeCheckError("quote retrieval timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def _positive_decimal(value: object) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise SmokeCheckError("quote price is not a valid decimal") from exc
    if not parsed.is_finite() or parsed <= 0:
        raise SmokeCheckError("quote price must be finite and positive")
    return parsed


def validate_quotes(
    payload: object,
    *,
    now: datetime | None = None,
    max_age: timedelta = MAX_QUOTE_AGE,
    future_skew: timedelta = MAX_FUTURE_SKEW,
) -> None:
    if not isinstance(payload, list) or len(payload) != len(EXPECTED_ASSETS):
        raise SmokeCheckError("market response must contain exactly four quote records")

    current_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    seen: set[str] = set()

    for quote in payload:
        if not isinstance(quote, dict):
            raise SmokeCheckError("market response contains a malformed quote")

        asset = quote.get("asset_id")
        if not isinstance(asset, str):
            raise SmokeCheckError("quote asset identifier is missing")
        asset = asset.strip().lower()
        if asset not in EXPECTED_ASSETS or asset in seen:
            raise SmokeCheckError("market response contains an unsupported or duplicate asset")
        seen.add(asset)

        if str(quote.get("currency", "")).lower() != "usd":
            raise SmokeCheckError(f"{asset} quote currency is not USD")
        _positive_decimal(quote.get("price"))

        if quote.get("source") != "coingecko":
            raise SmokeCheckError(f"{asset} quote provenance is not CoinGecko")

        retrieved_at = _parse_timestamp(quote.get("retrieved_at"))
        if retrieved_at > current_time + future_skew:
            raise SmokeCheckError(f"{asset} quote timestamp is too far in the future")
        if current_time - retrieved_at > max_age:
            raise SmokeCheckError(f"{asset} quote is older than the five-minute freshness limit")

    if seen != EXPECTED_ASSETS:
        raise SmokeCheckError("market response does not cover the required asset set")


def _request_json(base_url: str, path: str, bypass_secret: str) -> object:
    url = urljoin(base_url, path.lstrip("/"))
    headers = {
        "Accept": "application/json",
        "User-Agent": "veltrix-miner-staging-smoke/1.0",
        "x-vercel-protection-bypass": bypass_secret,
    }
    request = Request(url, headers=headers, method="GET")

    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            status = response.status
            final_url = response.geturl()
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        raise SmokeCheckError(f"{path} returned HTTP {exc.code}") from None
    except URLError as exc:
        raise SmokeCheckError(f"{path} network request failed ({type(exc.reason).__name__})") from None
    except TimeoutError:
        raise SmokeCheckError(f"{path} request timed out") from None

    base = urlsplit(base_url)
    final = urlsplit(final_url)
    if (final.scheme, final.hostname, final.port) != (base.scheme, base.hostname, base.port):
        raise SmokeCheckError(f"{path} redirected outside the configured staging origin")
    if status != 200:
        raise SmokeCheckError(f"{path} returned HTTP {status}")
    if len(raw) > MAX_RESPONSE_BYTES:
        raise SmokeCheckError(f"{path} response exceeded the size limit")

    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise SmokeCheckError(f"{path} did not return valid JSON") from None


def run_smoke_check(base_url: str, bypass_secret: str) -> None:
    normalized_url = normalize_base_url(base_url)
    if not bypass_secret.strip():
        raise SmokeCheckError("VERCEL_AUTOMATION_BYPASS_SECRET is not configured")

    checks = (
        ("/api/v1/health/live", validate_liveness, "liveness"),
        ("/api/v1/health/ready", validate_readiness, "database readiness"),
        (
            "/api/v1/market/quotes?assets=btc,xmr,ltc,doge",
            validate_quotes,
            "CoinGecko market quotes",
        ),
    )

    failures: list[str] = []
    for path, validator, label in checks:
        try:
            payload = _request_json(normalized_url, path, bypass_secret)
            if validator is validate_quotes:
                validator(payload, now=datetime.now(timezone.utc))
            else:
                validator(payload)
            print(f"PASS: {label}")
        except SmokeCheckError as exc:
            failures.append(f"{label}: {exc}")
            print(f"FAIL: {label}: {exc}")

    if failures:
        raise SmokeCheckError(f"{len(failures)} staging release check(s) failed")

    print("PASS: staging API satisfies the Phase 2 server-side smoke gates")


def main() -> int:
    base_url = os.environ.get("VELTRIX_STAGING_BASE_URL", "")
    bypass_secret = os.environ.get("VERCEL_AUTOMATION_BYPASS_SECRET", "")
    if not base_url.strip() or not bypass_secret.strip():
        print(
            "Configuration missing: set repository variable "
            "VELTRIX_STAGING_BASE_URL and Actions secret "
            "VERCEL_AUTOMATION_BYPASS_SECRET. No staging checks were run.",
            file=sys.stderr,
        )
        return 2

    try:
        run_smoke_check(base_url, bypass_secret)
    except SmokeCheckError as exc:
        print(f"Staging smoke verification failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
