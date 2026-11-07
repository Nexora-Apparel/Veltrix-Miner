# Phase 2.5 — Multi-Chain Recovery Intelligence

**Status:** Architecture proposal; not implemented, deployed, or validated.
**Base:** Android foundation branch `phase-2/android-app-foundation`.
**Purpose:** Identify legitimate, owner-authorized cryptocurrency recovery opportunities and quantify whether pursuing them is economically sensible.

## 1. Scope and non-goals

VELTRIX MINER may investigate:
- Unpaid mining-pool balances and rewards tied to an account the user owns or is authorized to administer.
- Protocol rewards, distributions, refunds, and claim mechanisms that are explicitly documented by the protocol.
- Owner-authorized wallet restoration using backups or recovery material handled locally by the owner.
- Mistaken transfers, wrong-network deposits, token-account configuration problems, and transaction tracing where a legitimate recovery route exists.
- Public blockchain activity that helps classify an address or transaction, without treating dormancy as ownership or permission.

The module must not:
- Guess, brute-force, derive, enumerate, or test private keys or seed phrases.
- Claim, sweep, transfer, freeze, or otherwise control funds from an address without documented owner authorization.
- Exploit smart contracts, validators, bridges, exchange systems, or wallet vulnerabilities.
- Describe a dormant, inactive, abandoned-looking, or inaccessible address as recoverable merely because it has a balance.
- Promise recovery, guaranteed profit, or a guaranteed payout.

USDT is not mined. It may appear as an asset in an authorized recovery investigation or as a settlement currency after a separately authorized, verified transaction.

## 2. Supported chain families

Initial adapter targets:
- Bitcoin: UTXO/address and transaction history; pool payout reconciliation.
- Solana: account and token-account activity; documented program rewards; owner-authorized account troubleshooting.
- TON: wallet and jetton activity; documented claim flows; owner-authorized investigation.
- EVM networks: ERC-20 and compatible token events, including USDT deployments where the exact chain and contract are verified.
- Additional chains only after adapter-specific threat modelling and test coverage.

An asset identity is always chain-specific. A ticker such as USDT is insufficient: persist chain ID/network, contract or mint address where applicable, decimals, and provider provenance.

## 3. Opportunity classification

Every finding must use one of these controlled classifications:
- `publicly_observable_not_claimable`: public data exists, but no legitimate claim route is established.
- `owner_authorized_recovery`: the owner has supplied authorization and the recovery path is documented.
- `protocol_claimable`: a protocol explicitly exposes a claim mechanism and eligibility can be independently verified.
- `unclaimed_pool_reward`: a pool reports a payable balance for an account the user controls.
- `potential_refund`: a documented refund or rent-return path may exist, subject to owner control and network rules.
- `manual_investigation`: evidence is incomplete or requires a provider, exchange, recipient, or protocol support process.
- `not_recoverable_by_current_evidence`: no supported recovery path is known.

A scanner must never upgrade an opportunity to claimable solely from address age, inactivity, balance size, or heuristic scoring.

## 4. System architecture

Read-only discovery pipeline:
1. `chain_registry`: canonical networks, chain IDs, native assets, token contract/mint registry, explorer/RPC provider configuration.
2. `address_watch`: public address watchlists; ownership/authorization metadata; no secret material.
3. `chain_adapters`: normalized read-only adapters for Bitcoin, Solana, TON, and EVM.
4. `event_ingestion`: transactions, transfers, pool statements, documented claims, and provider observations.
5. `recovery_rules`: deterministic rules tied to documented recovery mechanisms.
6. `evidence_engine`: source URLs/IDs, block height or logical time, observed timestamp, confidence, and reproducibility.
7. `opportunity_ledger`: immutable findings and state transitions.
8. `net_recovery_estimator`: estimated gross value less network fees, provider fees, recovery fees, conversion fees, and withdrawal costs.
9. `notification_service`: alert on newly evidenced opportunities and status changes.
10. `owner_action_handoff`: instructions and official protocol/provider links; user-controlled signing remains outside the backend.

The discovery service is read-only. It must not hold signing keys or submit asset-moving transactions.

## 5. Data model (proposed)

### recovery_watch_targets
- id, user_id, chain_id, address, label
- authorization_status, authorization_evidence_ref
- created_at, last_scanned_at
- Unique key: (user_id, chain_id, normalized_address)

### recovery_observations
- id, target_id, observation_type, asset_id
- transaction_id, block_height, observed_at
- provider_id, provider_reference, raw_evidence_hash
- confidence, created_at

### recovery_opportunities
- id, user_id, target_id, classification, status
- asset_id, gross_amount, gross_value_usd
- estimated_network_fee, estimated_service_fee, estimated_conversion_fee
- estimated_net_value_usd, estimate_timestamp
- evidence_summary, confidence, next_action
- created_at, updated_at

### recovery_authorizations
- id, user_id, target_id, authorization_type
- verification_status, evidence_reference, verified_at, expires_at
- Store references and verification metadata only; never store seed phrases or private keys.

### recovery_audit_events
- id, user_id, opportunity_id, actor, action
- before_state, after_state, timestamp, request_id

All monetary estimates must record currency, pricing source, quote timestamp, and whether values are indicative or executable.

## 6. Security and authorization

- No seed phrase, private key, keystore password, exchange password, or wallet recovery file may be sent to or stored by the backend.
- If wallet restoration is supported later, it must be an isolated, owner-operated local workflow with explicit security review. The first release only provides safe diagnostic guidance.
- Watch-only address tracking is the default.
- Authorization must be scoped to the exact account/address and action; authorization to inspect does not imply authorization to move funds.
- No automatic sweep, claim, conversion, or withdrawal.
- Any future transaction-signing feature requires a separate design review, explicit user confirmation, transaction preview, destination allowlisting, limits, and audit trail.
- Encrypt sensitive metadata in transit and at rest; apply least privilege, rate limits, abuse monitoring, and auditable access controls.

## 7. Recovery economics

For every opportunity:
`Estimated net recovery = verified gross recoverable amount - network fees - protocol/provider fees - conversion fees - withdrawal fees - other documented costs`

Do not count speculative balances, inaccessible balances, or unverified token prices as recoverable value. Show a range where fee or price uncertainty is material. Keep mining profitability and recovery proceeds in separate ledgers and dashboard totals.

## 8. API proposal

- `GET /api/v1/recovery/chains`
- `GET /api/v1/recovery/assets?chain_id=...`
- `POST /api/v1/recovery/watch-targets` (watch-only address registration)
- `GET /api/v1/recovery/watch-targets`
- `GET /api/v1/recovery/watch-targets/{id}/observations`
- `GET /api/v1/recovery/opportunities`
- `GET /api/v1/recovery/opportunities/{id}`
- `POST /api/v1/recovery/opportunities/{id}/request-review`
- `GET /api/v1/recovery/authorizations`

No API endpoint in this phase may sign, broadcast, sweep, or transfer funds.

## 9. Android integration

Add a Recovery area with:
- Chain and asset filters.
- Watch-only address management.
- Opportunity classification and evidence trail.
- Gross amount, estimated costs, net estimate, and quote timestamp.
- Clear status labels: Observed, Needs owner verification, Claim route verified, Manual review, Not claimable.
- Official next-step guidance.
- A permanent warning that public visibility does not confer ownership.

The screen must distinguish live provider observations from cached or unavailable data. Unknown values render as unavailable, never as zero or fabricated balances.

## 10. Verification gates

Before implementation can be called complete:
1. Unit tests for address normalization and chain/asset identity.
2. Adapter tests against fixtures and provider sandbox/testnet data.
3. Deterministic classification tests proving dormancy alone never creates a claimable opportunity.
4. Authorization tests proving unauthorized addresses cannot enter owner recovery workflows.
5. Security tests proving secrets are rejected and never logged or persisted.
6. Duplicate-ingestion and reorg/idempotency tests.
7. Fee and net-value calculation tests with timestamped prices.
8. End-to-end tests for watch-only discovery and evidence display.
9. Manual Android device test.
10. Independent review of each chain's documented recovery route before enabling it.

## 11. Delivery sequence

A. Approve and freeze this architecture.
B. Build chain registry and normalized asset identity.
C. Implement read-only Bitcoin adapter and fixture tests.
D. Add EVM token-event adapter with explicit network/contract verification.
E. Add Solana and TON adapters after provider selection and documented API review.
F. Implement opportunity rules, evidence ledger, and net-recovery estimator.
G. Add API and Android Recovery UI.
H. Run security, regression, provider, and physical-device verification.

**Current completion:** Architecture document only. No chain scanner, wallet recovery, reward claim, transaction signing, or production integration has been implemented.
