# Phase 1 — Repository Compatibility Audit

**Status:** Initial source audit completed; runtime verification outstanding  
**Audit date:** 2026-11-08  
**Target architecture:** Zero-cost, web-first control plane; Android companion; independently supervised mining workers only when suitable authorised compute exists  
**Spending limit:** ₦0

## Executive result

The repository contains useful foundations and should not be discarded wholesale. It does not currently implement actual mining, a complete web command centre, pool connectivity, worker telemetry, reward settlement, or a production-ready authenticated API.

The current implementation is a monitoring-oriented Android UI scaffold, a small FastAPI health/market API, a PostgreSQL readiness check, and CI workflows. No live worker or pool adapter was found in the inspected repository tree.

Do not describe the system as mining, earning, or launch-ready. The Phase 0 decision remains NO-GO for live mining because no suitable separate compute device has been identified.

## Component decisions

| Component | Decision | Evidence / rationale |
|---|---|---|
| Android Kotlin/Jetpack Compose application | KEEP | app/ contains a UI scaffold with dashboard, profitability, coin comparison, wallet and system screens. It explicitly shows unavailable/unconnected states and does not claim actual mining. |
| Android device telemetry | KEEP, MODIFY | Current UI reads battery percentage, model and Android version. It does not yet establish safe thermal monitoring or physical-device compatibility. |
| Android market API client | MODIFY | Retrofit/OkHttp and quote repository exist. The inspected MainActivity does not wire the repository into the visible UI; live market display is not complete. |
| FastAPI backend | KEEP | backend/app/main.py mounts versioned health and market routes. Clean foundation for read-only control-plane APIs. |
| Health endpoints | KEEP | Liveness is independent of database state; readiness returns 503 unless a real configured database answers SELECT 1. |
| CoinGecko quote adapter | KEEP, MODIFY | Read-only BTC/XMR/LTC/DOGE USD quote retrieval with decimal parsing and source/retrieval timestamps. Not a profitability engine; upstream plan/rate limits must be checked before relying on it. |
| PostgreSQL engine/readiness | MODIFY / HOLD | Connection code exists, but no dedicated VELTRIX MINER database has been verified. Do not reuse another project or provision a paid database. |
| Dockerfile | HOLD | Container build definition exists; no runtime deployment is required or authorised under the present feasibility gate. |
| Android CI | KEEP | Workflow builds debug APK and runs unit tests. Current audit did not independently execute the workflow. |
| Backend CI | KEEP | Workflow runs pytest. Current audit did not independently execute the workflow. |
| Vercel staging preparation (PR #7) | HOLD | PR documents a restricted SSO-protected staging project but explicitly says no deployment, dedicated database, or secret has been configured. Vercel runtime suitability and zero-cost status are not verified. |
| Web command centre | BUILD | No web frontend or web app entrypoint was present in the inspected root structure. The desired web-first interface remains unimplemented. |
| Mining worker / pool adapter | NOT PRESENT — BUILD LATER | No worker executable, pool protocol client, accepted-share telemetry, supervisor, or real worker heartbeat implementation was found in the inspected source tree. Phase 0 blocks implementation/activation. |
| Profitability engine | NOT PRESENT — BUILD LATER | Current UI lists required inputs but no mining profitability calculation backed by measured hardware power/hashrate and current network/pool data was found. |
| Rewards / earnings ledger | NOT PRESENT — BUILD LATER | No pool-confirmed reward ingestion or chain-confirmed payout verification found in inspected backend modules. |
| Wallet integration | KEEP AS READ-ONLY DESIGN | UI says no wallet is connected and private keys are never requested. No wallet signing or payout functionality found. |
| Recovery intelligence PR #2 | KEEP SEPARATE / DEFER | Documentation-only optional capability. It must not be coupled to mining execution or treated as an earnings source. |

## Findings by area

### Android application

Observed:
- Native Kotlin and Jetpack Compose.
- minSdk = 26, targetSdk = 34; JDK 17 and Kotlin JVM target 17.
- Internet permission only in the inspected manifest.
- Dashboard explicitly says no mining account is connected and no payout has been recorded.
- Worker count is displayed as zero/unconnected; hashrate and rewards are unavailable.
- Battery percentage is read through Android BatteryManager; model and Android version are displayed.
- UI text explicitly states temperature and detailed CPU telemetry are not inferred when unavailable.
- Retrofit/OkHttp market networking code exists under data/market, but visible screen integration was not found in MainActivity.kt.

Conclusion: preserve the Android application as the companion/control interface. Do not turn it into a sustained CPU miner.

### Backend

Observed:
- FastAPI service with /api/v1/health/live, /api/v1/health/ready, and /api/v1/market/quotes.
- Readiness requires a real configured PostgreSQL connection and a successful SELECT 1.
- Market quotes are retrieved from CoinGecko for a fixed allowlist: BTC, XMR, LTC and DOGE.
- Quote values use Python Decimal; missing/invalid upstream values cause explicit failure.
- No mining worker, pool, authentication/session, wallet, reward, or profitability endpoints are present in the inspected API tree.
- No persistent business schema or migration system was found in the inspected backend structure.

Conclusion: preserve FastAPI as the read-only API foundation. Add future API domains incrementally only when the zero-cost runtime and compute gates allow them.

### Infrastructure and CI

Observed:
- Root Dockerfile runs the FastAPI app as a non-root user.
- GitHub Actions workflows exist for Android build/unit tests and backend pytest.
- PR #7 prepares a Vercel staging entrypoint and SSO-restricted staging project, but says no deployment or dedicated database is provisioned.
- The repository has no confirmed production deployment URL in the inspected documentation.

Conclusion: retain workflows. Keep staging/deployment inactive until free-tier terms, sleep/timeout behaviour, resource use, database availability, SSO, and possible billing exposure are verified. Do not create a database or deploy a service that can incur charges.

## Architecture conflicts and corrections required

1. Web-first requirement: current repo is Android-first in its implemented UI. Add a lightweight web control plane as the primary user interface; Android remains companion.
2. Actual mining boundary: no mining process belongs in Vercel serverless functions or browser JavaScript. Worker execution requires a separate, persistent, compatible and authorised compute resource.
3. No-cost gate: any hosting, database, provider API or continuous runtime must be proven free for the intended workload. Free-tier availability is not evidence that persistent mining is permitted.
4. Data provenance: retain explicit source and retrieval timestamps. Unknown values remain unknown; estimated, pool-reported and chain-confirmed amounts must be separate.
5. Security: no private keys or seed phrases. Keep wallet tracking read-only. Do not expose unauthenticated control actions.
6. Profitability: no ranking or profit estimate until actual algorithm compatibility, measured worker hashrate/power, electricity cost, pool fees, payout threshold and conversion/withdrawal costs are available.

## Verification limitations

This is a source-tree and source-file audit using GitHub repository contents. It is not a local build, runtime penetration test, physical-device test, deployment test, or end-to-end pool test. CI workflow files were inspected but not executed in this audit. No production or staging resources were modified.

## Phase 1 disposition

- Preserve the Android scaffold, backend health/market foundation, and CI.
- Hold database and Vercel deployment work.
- Build the web control-plane frontend separately from worker execution.
- Defer worker implementation until suitable zero-cost authorised compute exists.
- Keep recovery intelligence separate and optional.
- Do not merge or deploy anything solely on the basis of this audit.

## Next engineering deliverable

Define the web-first control-plane contract and static UI shell with explicit UNCONFIGURED, UNKNOWN, STALE, and VERIFIED states. It must not imply a live worker, live earnings, or profitability where no verified source exists. Keep it buildable without paid hosting or database dependencies.
