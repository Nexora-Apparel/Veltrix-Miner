# Phase 2.2 — Live Backend Connectivity

## Objective
Connect the Android control application to a separately deployed VELTRIX MINER backend using authenticated HTTPS APIs. This phase is not complete until backend endpoints, Android integration, automated tests, and live-source freshness checks are verified.

## Dependencies and sequencing
- Phase 2.0 Android scaffold exists and has passed one CI debug build.
- Phase 2.1 physical-device validation remains an external gate for declaring device compatibility.
- Backend Phase 1 infrastructure is designed but not deployed. Do not point the Android app at a fictional endpoint or fabricate server responses.
- Implement transport and contract tests against a local mock server first; switch to staging only after a real backend URL and TLS configuration exist.

## Android architecture
Introduce these boundaries:
- `core/network`: HTTPS client, authentication interceptor, request IDs, bounded timeouts, structured error parsing.
- `core/model`: typed API response and error envelopes.
- `core/session`: access-token lifecycle; no credentials in source control or logs.
- `data/market`: market snapshot repository.
- `data/workers`: worker status repository.
- `data/wallet`: public-address and transaction-status repository.
- `data/settings`: persistent non-secret preferences.
- `domain/profitability`: calculation inputs and provenance-aware results.
- `feature/dashboard`: UI state mapping (Loading, Fresh, Stale, Unavailable, Error).

Use a repository pattern and inject API interfaces so UI composables never call HTTP directly. Keep network work off the main thread. Use bounded retries only for idempotent reads; never automatically retry financial writes or transaction submissions.

## API contract baseline
Base path: `/api/v1`. All timestamps are UTC ISO-8601 strings. All money values include asset symbol and decimal-safe string amounts; do not use binary floating-point for balances.

### Authentication
- `POST /auth/session` — exchange user credentials for a short-lived access token and refresh token according to the backend's session policy.
- `POST /auth/refresh` — rotate a refresh token.
- `POST /auth/logout` — revoke the active session.
- Store refresh material only in Android Keystore-backed encrypted storage. Never log tokens.

### Dashboard and market
- `GET /dashboard` — aggregated account summary with per-section source timestamps.
- `GET /market/assets` — supported asset metadata.
- `GET /market/snapshots?symbols=BTC, XMR, LTC, DOGE` — price, quote currency, provider, observedAt, receivedAt, and validity window.
- Reject malformed, future-dated, or stale snapshots. Display provider and last-updated time.

### Workers and pools
- `GET /workers` — registered worker status.
- `GET /workers/{workerId}` — detail and latest telemetry.
- `GET /pools` — configured pool metadata and connection health.
- `GET /workers/{workerId}/samples?from=&to=` — bounded telemetry history.
- Worker status must distinguish online, offline, stale, rejected, and unknown. A zero worker count is not proof of an active mining operation.

### Wallet and earnings
- `GET /wallets` — public-address tracking records.
- `POST /wallets` — register a public address with chain and ownership/authorization acknowledgement.
- `GET /wallets/{walletId}/transactions` — observed chain transactions and confirmation state.
- `GET /rewards` — estimated, pool-confirmed and chain-confirmed reward records as distinct types.
- `GET /earnings/summary` — settled earnings and costs with source references.
- The backend must never accept seed phrases or private keys. Address registration is not proof of ownership.

### Profitability
- `GET /profitability/opportunities` — candidates only when all required inputs are available.
- Each result includes algorithm, hardware profile, hashrate, measured power, tariff, pool fee, payout threshold, withdrawal/conversion costs, gross estimate, net estimate, currency, source timestamps, assumptions and confidence.
- Return `unavailable` with explicit missing-input reasons rather than inventing a ranking.

## Response envelope
Successful responses:
```json
{
  "data": {},
  "meta": {
    "requestId": "server-generated-id",
    "generatedAt": "2026-11-08T00:00:00Z",
    "source": "provider-id",
    "observedAt": "2026-11-08T00:00:00Z",
    "staleAfterSeconds": 60
  }
}
```

Errors:
```json
{
  "error": {
    "code": "AUTH_REQUIRED",
    "message": "Authentication is required.",
    "retryable": false
  },
  "meta": { "requestId": "server-generated-id" }
}
```

Do not expose stack traces, provider credentials, internal hostnames, or secrets in API errors.

## Data freshness policy
- Every provider-derived value carries source, observedAt, receivedAt and staleAfterSeconds.
- UI states: Loading, Fresh, Stale, Unavailable, Error.
- Stale data may be shown only with a visible stale label and timestamp; it must never be silently presented as live.
- A provider outage must not reset balances to zero.
- Missing source metadata means the value is unverified and cannot enter net-profit totals.

## Security requirements
- HTTPS only; reject cleartext traffic in production.
- No API secrets embedded in the APK.
- Short-lived access tokens and refresh-token rotation.
- Keystore-backed storage for session material.
- Redact authorization headers, addresses where appropriate, and all secrets from logs.
- Certificate validation enabled; no permissive trust manager.
- Rate limiting and server-side authorization on every account-scoped endpoint.
- Wallet APIs are read-only in this phase. No transaction signing, sweeping, conversion, or custody.
- No seed phrases or private keys in request bodies, analytics, crash reports or backend storage.

## Test plan
1. DTO serialization/deserialization tests, including missing and malformed fields.
2. API contract tests for success, authentication failure, rate limit, timeout and provider outage.
3. Staleness tests using fixed clocks and boundary timestamps.
4. Repository tests proving stale/unavailable values cannot be counted as confirmed earnings.
5. UI state tests for Loading, Fresh, Stale, Unavailable and Error.
6. Security tests ensuring tokens are redacted and cleartext endpoints rejected.
7. Integration tests against a local mock server; then staging backend.
8. Physical-device network lifecycle tests on Android 11, including loss and restoration of connectivity.

## Acceptance gates
- [ ] Backend staging environment exists and health endpoint is verified.
- [ ] Authentication and authorization tests pass.
- [ ] Android typed API client and repositories compile and pass tests.
- [ ] Live market values show provider and source timestamp.
- [ ] Stale data is visibly marked and excluded from live profitability.
- [ ] Worker states are sourced from a real pool/worker adapter.
- [ ] Wallet transaction states are independently chain-verified.
- [ ] Settings persist across process restart without storing secrets insecurely.
- [ ] No fabricated balances, rewards, hashrate or profitability.
- [ ] Android 11 integration tests pass.

Phase 2.2 remains IN PROGRESS until all applicable gates have evidence. Architecture documentation alone does not satisfy this phase.
