# Recovery Chain Registry — Phase 2.5 Component A

**Status:** Design specification only. No RPC provider, contract address, or live chain integration has been configured.

## 1. Design rule

A ticker or display symbol is never a unique asset identifier. The canonical identity is the tuple:

`(namespace, network_id, asset_reference)`

- Bitcoin native BTC: namespace `bitcoin`, network `mainnet`, asset reference `native`.
- Solana native SOL: namespace `solana`, network `mainnet-beta`, asset reference `native`.
- TON native Toncoin: namespace `ton`, network `mainnet`, asset reference `native`.
- EVM native assets: namespace `eip155`, network ID is the numeric EVM chain ID, asset reference `native`.
- Contract/mint assets: asset reference is the verified contract or mint address, scoped to its network.

USDT entries must be separate per network and exact token contract. Never infer a contract from the symbol alone.

## 2. Registry record

Required fields:
- `namespace`: protocol namespace.
- `network_id`: stable network identifier.
- `display_name`: human-readable network label.
- `environment`: `mainnet`, `testnet`, or `devnet`.
- `asset_reference`: `native` or exact contract/mint address.
- `symbol`, `name`, `decimals`.
- `asset_type`: `native`, `fungible_token`, or `other`.
- `verification_status`: `unverified`, `verified`, or `deprecated`.
- `verification_sources`: authoritative chain/protocol references.
- `effective_from`, `last_verified_at`.

Optional provider configuration must be stored separately from canonical identity. API credentials must be held in a secret manager, never in this registry or source control.

## 3. Initial network entries (identity only)

| Namespace | Network ID | Native asset | Status |
|---|---|---|---|
| bitcoin | mainnet | BTC | Identity defined; provider not selected |
| solana | mainnet-beta | SOL | Identity defined; provider not selected |
| ton | mainnet | TON | Identity defined; provider not selected |
| eip155 | chain ID required | Native gas asset | Per-network verification required |

No USDT contract is pre-populated. Each candidate deployment must be independently checked against official issuer documentation and the relevant chain's authoritative registry/explorer before activation.

## 4. Validation rules

1. Reject unknown namespace/network combinations.
2. Reject EVM assets without a numeric chain ID.
3. Validate token address format and checksum where the chain defines one.
4. Preserve case-sensitive address semantics where required; normalize only according to chain-specific rules.
5. Reject symbol-only asset lookup for balances, valuation, or recovery eligibility.
6. Keep testnet/devnet records isolated from mainnet accounting.
7. A deprecated contract remains in historical records but cannot be used for new recovery recommendations.
8. Require at least two independent authoritative checks before setting a token deployment to `verified`.
9. Store decimals from authoritative token metadata; do not infer decimals from ticker conventions.
10. Record registry changes as append-only audit events.

## 5. Proposed database tables

### chain_networks
`id, namespace, network_id, display_name, environment, native_asset_reference, status, created_at, updated_at`

Unique: `(namespace, network_id)`.

### chain_assets
`id, namespace, network_id, asset_reference, symbol, name, decimals, asset_type, verification_status, effective_from, last_verified_at`

Unique: `(namespace, network_id, asset_reference)`.

### chain_asset_sources
`id, asset_id, source_type, source_reference, checked_at, evidence_hash, reviewer_status`

### chain_providers
`id, namespace, network_id, provider_name, endpoint_secret_ref, enabled, health_status, last_checked_at`

The endpoint secret reference points to a secret manager entry. Raw API keys are not stored in application tables.

## 6. Acceptance tests

- BTC on Bitcoin mainnet cannot collide with a token named BTC on another network.
- USDT on two different EVM networks produces two different asset IDs.
- Same contract address on different chain IDs produces different asset IDs.
- A symbol-only query cannot return a verified recovery target.
- Testnet assets never enter mainnet portfolio totals.
- Unverified or deprecated assets cannot produce a claimable recovery opportunity.
- Provider outages do not silently convert unknown balances to zero.
- Registry modifications are auditable and reproducible.

## 7. Exit criteria

The registry component is ready for implementation only after:
- authoritative network identifiers are documented,
- provider candidates and their data rights/limits are reviewed,
- official token contract/mint references are verified,
- normalization and uniqueness tests are agreed,
- secrets management is available.

**Current result:** Canonical identity rules and acceptance criteria documented. Live registry and provider connections remain unimplemented.
