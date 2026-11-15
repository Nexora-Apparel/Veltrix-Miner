# VELTRIX MINER — Cloudflare application deployment

This package is the zero-cost application-hosting adapter. It does **not** run mining jobs.

## Runtime layout

- Cloudflare Worker handles the small read-only API surface.
- Workers Static Assets serves the existing `web/` dashboard from the same deployment.
- D1 is used only for a read-only readiness probe and the schema-version marker at this stage.
- The existing FastAPI + PostgreSQL backend remains the local/reference implementation; it is not silently migrated or deleted.
- No wallet signing, private-key storage, browser mining, WASM mining, scheduled compute or persistent mining worker is present.

The Worker deliberately uses the existing API paths and response shapes:
- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`
- `GET /api/v1/market/quotes?assets=btc,xmr,ltc,doge`

Market data is fetched from the fixed CoinGecko endpoint. A demo API key is optional and must be stored as a Worker secret, never in `web/` or `wrangler.jsonc`. Missing/incomplete provider data returns 503; it is never replaced with cached or invented values.

## Free-tier and zero-spend controls

1. Use the Cloudflare Workers Free plan and D1 Free plan only.
2. Do not enable Workers Paid, D1 paid overages, paid observability, paid add-ons or a paid domain.
3. Keep `workers_dev` enabled; no custom domain is required.
4. The Worker is request-driven and must not be used for mining or continuous background work.
5. No resource has been created and no deployment has been performed by this repository change.

Cloudflare may change quotas or plan terms. Check the account's current plan and free quotas before creating resources. Stop if the dashboard asks for a payment method, upgrade, billing activation or paid feature.

## One-time setup (manual Cloudflare account action required)

1. Sign in to a Cloudflare account and confirm Workers Free is active.
2. From the repository root, create the D1 database:
   ```sh
   npx wrangler d1 create veltrix-miner
   ```
3. Copy the returned database ID into `wrangler.jsonc`, replacing the explicit placeholder.
4. Apply the initial schema:
   ```sh
   npx wrangler d1 migrations apply veltrix-miner --remote
   ```
5. Deploy only after reviewing the generated plan and confirming no paid feature is enabled:
   ```sh
   npx wrangler deploy
   ```
6. Set the web console API origin to the resulting `workers.dev` URL in a reviewed frontend config change. If the console and API share the same origin, leave `WEB_ORIGIN` empty; configure one exact HTTPS origin only when cross-origin browser access is genuinely required.

Do not put account tokens, D1 credentials, wallet secrets or provider keys in Git. If a CoinGecko demo key is available, configure it using `wrangler secret put COINGECKO_DEMO_API_KEY`.

## Local verification

Run the dependency-free Worker contract tests with Node.js 20 or later:

```sh
node --test cloudflare/tests/worker.test.mjs
```

The tests use mocked D1 and upstream market responses. They verify API contracts and failure handling; they do not prove a live Cloudflare deployment, D1 account binding, CoinGecko availability, or end-to-end production readiness.

## Explicitly deferred

- Authentication and operator roles.
- Persistent operational data models and writes.
- Pool adapters, worker heartbeats and share accounting.
- Rewards, payout and verified earnings ledger.
- Mining compute and scheduled execution.

These remain deferred until their security, data provenance and Phase 0 feasibility gates pass.
