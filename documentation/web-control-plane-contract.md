# VELTRIX MINER — Web Control-Plane Contract

**Status:** Architecture contract; no frontend implementation or live service implied  
**Architecture:** Web-first control plane; Android companion; worker execution isolated  
**Cost rule:** Must remain usable as a local/static frontend without paid hosting, database, or API dependencies.

## 1. Responsibility boundaries

### Web control plane
- Primary operator interface for overview, market research, profitability inputs, worker inventory, pool configuration, telemetry, verified earnings, audit history and system configuration.
- Displays data provenance, timestamps, freshness and explicit unknown/unconfigured states.
- Sends authenticated, authorised control requests only to a separately supervised worker service after that capability is implemented and approved.
- Must not perform proof-of-work mining in browser JavaScript or keep a mining process alive in a browser tab.

### Android companion
- Notifications, read-only status, device diagnostics, and secure operator access.
- No sustained mining workload on the Realme 5 Pro.
- No private keys or seed phrases.

### Worker plane
- Runs only on compatible, persistent, explicitly authorised compute.
- Connects directly to a selected pool/protocol endpoint.
- Reports worker identity, algorithm, observed hashrate, accepted/rejected/stale shares, uptime, power measurements and heartbeat.
- Must be independently supervised; web/API restarts must not be mistaken for worker restarts.
- Not implemented and not authorised while Phase 0 remains NO-GO.

## 2. Global data-state vocabulary

| State | Meaning | Display rule |
|---|---|---|
| UNCONFIGURED | No source or connection has been configured. | Show setup-needed; never substitute zero. |
| UNKNOWN | A value cannot be established or validated. | Show unknown with reason where possible. |
| STALE | Previously sourced data exceeds its freshness window. | Show value only with stale label and timestamp; exclude from live decisions. |
| VERIFIED | Source, timestamp and validation requirements passed. | Show source and last-verified time. |
| ERROR | A source request or validation failed. | Show failure; retain last-known data only as STALE. |
| DISABLED | Capability intentionally unavailable or gated. | Explain why it is disabled. |

Absence of a worker record is not a zero-hashrate measurement. A missed heartbeat must transition a worker to STALE or OFFLINE, never RUNNING. A provider outage must not reset wallet balances or earnings to zero.

## 3. Initial navigation

1. Overview — overall system state, data freshness, verified net earnings (only if independently settled), worker inventory and alerts.
2. Market — provider-sourced asset quotes and network parameters with provenance.
3. Profitability — scenario analysis only when all required inputs are available.
4. Workers — registered workers, heartbeat, pool shares and measured telemetry; default UNCONFIGURED.
5. Pools — pool metadata, fees, payout threshold, connection state and terms.
6. Earnings — estimated, pool-confirmed and blockchain-confirmed records kept separate.
7. Costs — electricity, data, pool, withdrawal and conversion cost inputs.
8. Audit — immutable event history for configuration changes, worker state transitions and reward reconciliation.
9. Settings — user preferences and security; no secret or seed phrase fields.

## 4. API contract boundary

Existing endpoints:
- GET /api/v1/health/live — process liveness only.
- GET /api/v1/health/ready — readiness only when a real configured database check succeeds.
- GET /api/v1/market/quotes?assets=btc,xmr,ltc,doge — provider-sourced market information only.

Future endpoint families (not implemented):
- GET /api/v1/dashboard — aggregated status with per-section provenance.
- GET /api/v1/workers and GET /api/v1/workers/{worker_id} — worker inventory and status.
- GET /api/v1/workers/{worker_id}/samples — bounded telemetry history.
- GET /api/v1/pools — configured pool metadata and connection health.
- GET /api/v1/profitability/opportunities — candidate scenarios with explicit assumptions and missing-input reasons.
- GET /api/v1/rewards — separate estimated, pool-confirmed and chain-confirmed reward records.
- GET /api/v1/earnings/summary — reconciled settled earnings and itemised costs.
- GET /api/v1/audit — operator-visible audit history.

Future worker-control commands, if ever introduced, require authentication, role checks, CSRF protection where applicable, idempotency, replay protection, audit records, explicit worker identity and a hard stop mechanism. They are intentionally excluded from this initial read-only contract.

## 5. Data model invariants

- All timestamps are UTC ISO-8601.
- All currency quantities are decimal strings with an explicit asset/currency code; do not use binary floating point for money.
- Every external value carries source, observed_at, received_at and freshness policy.
- Every worker sample carries worker_id, algorithm, sample timestamp, source agent/version and measurement method.
- Hashrate must be accompanied by algorithm and measurement window.
- Power draw must be measured at the worker/system boundary or explicitly marked estimated; estimated power cannot be labelled measured.
- Pool shares distinguish accepted, rejected, stale and pending.
- Reward state distinguishes estimated, pool-confirmed, paid, and blockchain-confirmed.
- Net earnings are not calculated until all attributable costs and conversion assumptions are supplied.
- Missing cost is UNKNOWN, not zero.

## 6. Profitability eligibility

A profitability result is unavailable unless all material inputs exist:
- Exact coin/algorithm and compatible hardware profile.
- Verified or explicitly labelled benchmark hashrate for that hardware and algorithm.
- Measured or explicitly labelled estimated power draw.
- Network difficulty/hashrate and block reward or equivalent network parameters with timestamps.
- Pool fee and payout threshold/terms.
- Electricity tariff and duty cycle.
- Mobile/broadband data marginal cost where material.
- Withdrawal, conversion and settlement costs.
- Current asset price and intended settlement currency.

Output must separate gross expected reward, operating costs, net estimate, uncertainty, source timestamps and assumptions. Never promise a return or label an estimate as earned income.

## 7. Zero-cost implementation constraints

- First deliverable is a static web shell that can be previewed locally or built in CI; it must not require a production server to demonstrate its state model.
- Do not add paid hosting, managed database, paid API, subscription, external monitoring or cloud compute.
- Do not enable any resource that can incur a charge without a separately verified zero-cost path and billing guard.
- Public provider access is optional and must fail closed when rate-limited/unavailable; the UI must remain useful in offline/unknown mode.
- Do not add a continuous polling loop by default. Use manual refresh or bounded, visible refresh intervals once a real API exists.

## 8. Acceptance tests for the first web shell

- Renders without a backend, database, or secret.
- Every live-data panel defaults to UNCONFIGURED or UNKNOWN, never fabricated data.
- Simulated examples, if used in design tests, are visibly marked DEMO and excluded from totals.
- No browser mining code, WebAssembly miner, background compute loop, or hidden resource consumption.
- No private-key, seed-phrase or wallet-signing form.
- Worker cannot be shown RUNNING without a fresh authenticated worker heartbeat.
- Stale source data is visibly marked and excluded from profitability and verified earnings.
- Keyboard navigation and small-screen layout are usable.

## 9. Current implementation gate

Phase 0 currently blocks live mining because no separate suitable compute resource is available. The web shell may be developed as a zero-cost, read-only control-plane interface. Worker APIs, persistent database setup and production deployment remain deferred until their own feasibility and zero-cost gates pass.
