# VELTRIX MINER — Phase 1 Web/API Integration Contract

**Status:** Implemented in the Phase 1 branch; runtime validation pending  
**Cost:** No additional service or subscription  
**Execution:** Manual, bounded, read-only requests only

## 1. Existing backend endpoints reused

| Endpoint | Success contract | UI treatment |
|---|---|---|
| `GET /api/v1/health/live` | `status=alive`, service, version | API service is VERIFIED only after schema validation |
| `GET /api/v1/health/ready` | `status=ready`, `database=connected` | Database is VERIFIED only after the backend's `SELECT 1` succeeds |
| `GET /api/v1/market/quotes?assets=btc,xmr,ltc,doge` | Array of USD quotes with decimal-string prices, source and retrieval timestamps | Each quote is shown only after schema, provenance and freshness validation |

No new backend data endpoints are required for this integration slice.

## 2. Frontend request policy

- The public API origin is configured in `web/config.js`; it is empty by default.
- The API origin must be HTTPS remotely. HTTP is accepted only for localhost development.
- The base URL must be an origin, not a path, and cannot contain credentials, query parameters or fragments.
- Requests occur only after the operator presses **Refresh data**.
- No startup fetch, automatic polling, background worker, local storage, credentialed fetch or browser secret storage.
- Each request has a 6.5-second timeout, uses `cache: no-store`, omits credentials and rejects redirects/non-JSON responses.
- The UI reports API service, database readiness and market quote results independently.

## 3. Quote validation

Every returned quote must satisfy:
- Asset belongs to the requested BTC/XMR/LTC/DOGE allowlist.
- Currency is USD.
- Price is a positive decimal string.
- Source is exactly `coingecko`.
- `retrieved_at` is a parseable timestamp no more than 2 minutes old and no more than 60 seconds in the future.
- Optional market-cap, volume and 24-hour-change values are decimal strings or null.
- All four requested assets are present exactly once.

If the response is incomplete or any quote fails validation, the market set is rejected as a whole. The UI displays no partial/cached values as current data. Stale data is labelled STALE; missing configuration is UNCONFIGURED; request/schema/provider failures are ERROR or UNAVAILABLE.

The timestamp is the backend retrieval time, not an exchange execution timestamp. A verified quote is market information only and is not proof of mining profitability.

## 4. Cross-origin security

Backend `WEB_ORIGIN` is optional and unset by default. When set:
- It must be one exact HTTPS origin (localhost HTTP is allowed for development).
- CORS allows only that origin.
- Only GET is allowed.
- Only the Accept request header is allowed.
- Credentials are disabled.
- Wildcard origins, URL paths, query strings, fragments and embedded credentials are rejected.

Same-origin deployments do not require CORS. CORS is not authentication; future private/operator endpoints still require a separate authentication and authorisation design.

## 5. Known blockers

- No production API origin is configured.
- No database URL has been independently verified for this project.
- CoinGecko requests have not been executed from the deployed frontend.
- Cross-origin CORS has not been exercised against a deployed service.
- Browser/device QA and CI execution are pending.

This implementation does not enable mining, worker control, profitability estimates, earnings accounting or wallet operations.
