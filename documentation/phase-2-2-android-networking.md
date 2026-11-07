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
