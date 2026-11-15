# VELTRIX MINER — Phase 1: Zero-Cost Architecture Baseline

**Status:** In progress — architecture decision record  
**Baseline:** 2026-11-08  
**Repository:** Nexora-Apparel/Veltrix-Miner  
**Hard constraint:** ₦0 new spending. No paid services, subscriptions, hardware purchases, deposits, or paid API dependencies.

## 1. Product objective

Build a legitimate mining operations and profitability platform. The system must distinguish market estimates from actual mining activity and independently verifiable rewards. It must never fabricate hashrate, worker uptime, balances, accepted shares, rewards, or payouts.

The optimisation target is sustainable net proceeds, expressed in USDT where conversion is available:

`net = realised mining rewards - pool fees - electricity - hardware depreciation - network and conversion fees`

Unknown costs must remain explicitly unknown; they must not be silently treated as zero.

## 2. Web versus Android decision

The **web application is the primary command centre** for configuration, monitoring, profitability analysis, worker management, and audit history.

The **Android application is the companion control surface** for alerts, worker status, safe start/stop requests, and read-only monitoring. The Realme 5 Pro is not assumed to be profitable mining hardware.

Neither a normal browser tab nor a Vercel serverless function is a suitable persistent mining worker. Browser mining is not the production execution strategy: it is throttled, lifecycle-dependent, thermally constrained, and unreliable when the tab closes or the device sleeps.

## 3. Plane separation

### Control plane
- Web dashboard and authenticated API.
- Android companion client.
- User settings, worker registration, policy and safety controls.
- Profitability calculations, reporting, and audit ledger.
- Read-only market and network metadata integrations where free tiers permit.

### Execution plane
- A separately supervised mining worker on compatible compute.
- Worker connects directly to a supported pool or protocol endpoint.
- Worker reports signed/identifiable telemetry: algorithm, coin, pool, worker ID, hashrate samples, accepted/rejected shares, uptime, and payout references.
- Worker credentials are scoped and never include wallet private keys.

The control plane may request worker actions, but it does not perform proof-of-work itself. Execution must remain possible without keeping a browser open.

## 4. Zero-cost operating policy

- No paid cloud compute, paid databases, paid APIs, paid monitoring, or paid domains.
- No deployment or resource that can create a bill without an explicit cost review.
- Existing free-tier resources may be used only after checking limits, data retention, sleep behaviour, and terms.
- No reliance on a free tier for continuous mining compute unless its provider explicitly permits that workload and it remains available without payment.
- Do not use another person's device, account, electricity, or compute without explicit authorisation.
- No real-money deposits or automatic asset transfers.
- Wallet private keys and seed phrases are never collected or stored.

**Important feasibility boundary:** ₦0 software development does not guarantee ₦0 mining operations. Actual mining requires compute, network access, and usually electricity. If no suitable already-owned/authorised compute resource is available, the platform can be built and tested in read-only mode, but real mining cannot honestly be claimed to be active.

## 5. Initial technical architecture

- **Web:** responsive dashboard; static/client UI where practical.
- **API:** FastAPI service for authentication, configuration, worker registration, telemetry ingestion, profitability, and ledger queries.
- **Database:** PostgreSQL schema, introduced only when a genuinely free and isolated database is confirmed.
- **Android:** Kotlin/Jetpack Compose client using the same versioned API contract.
- **Worker agent:** independent process/service; algorithm-specific adapters kept outside the API service.
- **Observability:** structured logs, health/readiness checks, event timestamps, and worker heartbeat expiry.
- **Deployment:** no production deployment in this phase. Vercel may host control-plane API/UI routes only if free-tier limits and runtime compatibility are verified. It must not host persistent workers or Stratum sessions.

## 6. Data integrity and security requirements

- Separate estimated revenue, observed telemetry, pool-reported rewards, and confirmed wallet payouts.
- Every financial record carries source, timestamp, asset, quantity, status, and verification evidence.
- Idempotent ingestion prevents duplicate shares, payouts, and ledger entries.
- Stale worker heartbeat means UNKNOWN/OFFLINE, never RUNNING.
- Missing market prices or costs produce UNKNOWN/UNVERIFIED outputs, not fabricated zeroes.
- Wallet addresses are public identifiers; private keys and seed phrases are prohibited.
- Authenticated worker tokens are revocable, scoped, and stored as hashes where feasible.
- API readiness must not imply that a miner is running.

## 7. First supported operating mode

Phase 1 does not select a coin or claim profitability. It defines the platform and the acceptance gates. The first real worker can only be selected after verifying:
1. The user's already-owned and authorised compute resources.
2. Supported algorithms and operating-system compatibility.
3. Pool access and payout thresholds.
4. Power draw and actual electricity cost.
5. Thermal, battery, and device-wear risks.
6. A measurable path to positive net proceeds.

The Realme 5 Pro remains a control device by default. Do not run sustained mining workloads on it without a separate thermal, power, and net-profit feasibility test.

## 8. Phase 1 deliverables

- [x] Establish control-plane versus execution-plane separation.
- [x] Establish web-first command-centre / Android companion roles.
- [x] Prohibit serverless/browser execution as persistent mining workers.
- [x] Define zero-cost and no-private-key policies.
- [x] Define telemetry, earnings provenance, and audit requirements.
- [ ] Inventory existing repository code and classify reusable, isolated, or prohibited components.
- [ ] Confirm free-tier constraints before enabling any external service.
- [ ] Define API contracts and database schema.
- [ ] Approve a first worker only after compute, power, pool, and thermal feasibility checks.
- [ ] Pass architecture review before production implementation.

## 9. Explicit non-goals

- No simulated mining or fake balances.
- No cloud-mining rental or guaranteed-profit claims.
- No browser tab as the persistent miner.
- No mining process inside Vercel serverless functions.
- No wallet custody, seed phrase collection, or private-key handling.
- No paid infrastructure or purchases under the current budget constraint.

## 10. Relationship to existing work

The existing Android scaffold, FastAPI API work, CI workflow, and documentation may be reused after audit. They are not evidence of live mining. The Vercel staging preparation must remain undeployed until its cost, runtime, and database isolation gates are met. Existing recovery-intelligence work is a separate optional module and must not be allowed to expand Phase 1 scope.

No existing PR is merged as part of this architecture baseline. Review and merge decisions remain separate release gates.
