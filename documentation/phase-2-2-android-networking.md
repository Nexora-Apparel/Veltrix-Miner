# Phase 2.2 — Android networking foundation

## Implemented
- Retrofit/OkHttp client with pinned dependency versions.
- HTTPS-only endpoint validation. Cleartext HTTP, embedded URL credentials, query strings and fragments are rejected.
- API base URL is supplied through the Gradle property `VELTRIX_API_BASE_URL`; it defaults to an empty string.
- Market quote DTO uses `BigDecimal` for decimal values and retains provider source and API retrieval timestamp.
- Repository exposes explicit outcomes for unconfigured endpoint, HTTP failure, network failure, invalid response and success.
- Android INTERNET permission is declared.

## Configure a staging build
Use a real HTTPS staging origin only after the backend is deployed and reachable:

```bash
./gradlew assembleDebug -PVELTRIX_API_BASE_URL=https://your-staging-host.example/
```

The example hostname is a placeholder, not a deployed Veltrix endpoint. Do not commit staging credentials or production secrets. Do not configure an HTTP endpoint.

If the property is omitted, the repository returns `NotConfigured`. The client does not invent prices, cache stale prices as fresh, or treat API retrieval time as exchange trade time.

## API contract
`GET /api/v1/market/quotes?assets=btc,xmr,ltc,doge`

Expected fields per quote:
- `asset_id`, `currency`, `price`
- optional `market_cap`, `volume_24h`, `change_24h_pct`
- `source`, `retrieved_at`

The backend currently reports `retrieved_at` as API retrieval time. This client preserves it as a timestamp string; it does not claim that it is an exchange trade timestamp.

## Deliberately not connected yet
- No UI price rendering or profitability ranking.
- No persistent cache or stale-data policy.
- No authentication/session token handling.
- No production endpoint or database.
- No worker control, wallet signing, payouts or conversion.

## Verification still required
- Android Gradle CI on this branch.
- Contract test against a deployed staging backend.
- TLS certificate and endpoint verification.
- Physical Realme 5 Pro network and lifecycle tests.


## Quote freshness and integrity gate

The repository now classifies responses using an injectable UTC clock:
- `Fresh`: every requested asset is present exactly once, has a positive USD price, a source, and a valid ISO-8601 timestamp no older than five minutes.
- `Stale`: quote structure is valid, but the oldest quote exceeds the five-minute freshness window. Stale quotes are returned in a separate result type and must not be used for profitability calculations.
- `InvalidResponse`: missing/duplicate/unrequested assets, non-USD currency, non-positive price, malformed timestamp, or a timestamp more than 60 seconds in the future.
- `NotConfigured`, `HttpFailure`, and `NetworkFailure`: no quote data is represented as current.

The five-minute threshold is an initial client-side policy, not a claim that the upstream provider updates every asset at that frequency. It should be tuned using observed provider cadence before production. The API's `retrieved_at` is the backend retrieval timestamp, not the exchange's trade timestamp.

JVM tests cover fresh/stale classification, future timestamps, missing and duplicate assets, currency and price validation. These tests and the Android build must pass in CI before this component is accepted.
