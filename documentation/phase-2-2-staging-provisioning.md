# VELTRIX MINER — restricted staging provisioning

## Provisioned

- Vercel project: `veltrix-miner-staging`
- Framework: FastAPI
- Root directory: `backend/`
- Git repository: `Nexora-Apparel/Veltrix-Miner`
- Deployment protection: Vercel SSO protection enabled for all deployment URLs
- Preview deployments: disabled at project level

The project exists but has not yet been deployed. No staging hostname or deployment URL is valid until the first successful deployment completes.

## Deployment entrypoint

`backend/index.py` exports `app` from `app.main` for Vercel's Python ASGI runtime. The Vercel project root must remain `backend/`.

## Required secrets and database

Set these only in the Vercel project environment-variable manager, scoped to the Staging environment where supported:

- `ENVIRONMENT=staging`
- `DATABASE_URL=postgresql+psycopg://...` (sensitive)
- `COINGECKO_BASE_URL=https://api.coingecko.com`
- `COINGECKO_API_KEY` (optional; sensitive)

Do not put database credentials or provider keys in GitHub, source files, Android BuildConfig, APK resources, or chat messages.

## Database selection gate

The connected Neon account currently exposes two existing projects, neither identified as VELTRIX MINER. Do not reuse either project or its credentials without confirming ownership and intended purpose. Provision a dedicated VELTRIX MINER staging database or identify a dedicated existing one. Prefer a dedicated staging branch/database isolated from production data.

## Release verification

1. Deploy the merged backend to Vercel Staging with SSO protection still enabled.
2. Configure the dedicated staging `DATABASE_URL` and redeploy.
3. Verify `GET /api/v1/health/live` returns HTTP 200.
4. Verify `GET /api/v1/health/ready` returns HTTP 200 and reports `database=connected`; the endpoint must return 503 otherwise.
5. Verify `GET /api/v1/market/quotes?assets=btc,xmr,ltc,doge` returns current provider-sourced USD quotes with source and retrieval timestamps. A provider outage must remain an explicit 503, never a fabricated quote.
6. Confirm SSO protection remains enabled on every staging deployment URL.
7. Only after those checks, build Android with `-PVELTRIX_API_BASE_URL=https://<verified-staging-host>/` and run the Android-to-staging contract test.

## Security boundary

The API currently exposes read-only market quotes and health endpoints. It has no account authentication, user data, mining-worker control, wallet signing, payout or conversion endpoints. SSO protection is therefore required for the staging deployment while the Android client contract is being verified. Do not disable SSO or promote this service to production as part of Phase 2.2.

## Current blockers

- Dedicated VELTRIX MINER staging PostgreSQL database and connection string are not provisioned.
- The first Vercel deployment has not run; no HTTPS staging hostname has been verified.
- CoinGecko live-provider response has not yet been tested through the deployed backend.
- Android must not be configured with a guessed or unverified base URL.
