# VELTRIX MINER — restricted staging provisioning

## Deployment inventory (verified 2026-11-11)

- Vercel project: `veltrix-miner-staging`
- Project ID: `prj_MnNQyCZj6L1EAKqFNjfpljOo2xjQ`
- Framework: FastAPI
- Root directory: `backend/`
- Git repository: `Nexora-Apparel/Veltrix-Miner`
- Latest inspected deployment: `veltrix-miner-staging-p9w5napaz-nexora-apparel.vercel.app`
- Deployment target/state: `staging / READY`
- Deployment protection: Vercel SSO protection enabled for all deployment URLs
- Preview deployments: disabled at project level

The deployment is real and responds over HTTPS. A Vercel-authenticated deployment fetch was used for smoke checks; this does not make the protected deployment directly accessible to an unauthenticated Android client.

## Live smoke-check results (2026-11-11)

| Endpoint | Observed result | Interpretation |
|---|---|---|
| `GET /api/v1/health/live` | HTTP 200, `status=alive` | Application process is responding |
| `GET /api/v1/health/ready` | HTTP 503, `database=not_configured` | Staging database gate fails |
| `GET /api/v1/market/quotes?assets=btc,xmr,ltc,doge` | HTTP 200, four USD quote records | Live backend-to-CoinGecko path responds |

The four market records contained the expected asset identifiers, USD currency, positive decimal price fields, `source=coingecko`, and `retrieved_at` timestamps. No prices are committed to source control or treated as persistent project state. The market endpoint's success does not override the failed database-readiness gate.

## Deployment entrypoint

`backend/index.py` exports `app` from `app.main` for Vercel's Python ASGI runtime. The Vercel project root must remain `backend/`.

## Environment and database

The non-decrypted Vercel environment inventory returned only `COINGECKO_BASE_URL` and `ENVIRONMENT`, both scoped to Production. No `DATABASE_URL` was present, and no staging-scoped variables were returned. The Vercel project has no custom environment named `staging`: the custom-environment list was empty and filtering environment variables by slug `staging` returned not found. The deployment record's `target=staging` label does not substitute for a configured custom environment with staging-scoped variables.

The connected Neon account search returned no project named for VELTRIX MINER. The existing `VELTRIXFOOTBALL` project is unrelated and must not be reused for this service.

Required configuration, managed only in the hosting/database secret managers:

- `ENVIRONMENT=staging`
- `DATABASE_URL=postgresql+psycopg://...` (sensitive; never commit or paste into chat)
- `COINGECKO_BASE_URL=https://api.coingecko.com`
- `COINGECKO_API_KEY` (optional; sensitive)

Provision a dedicated VELTRIX MINER staging PostgreSQL project/database or identify an already-provisioned database explicitly dedicated to this service. Do not reuse unrelated project credentials or production data.

## Protected staging smoke workflow

A fail-closed, manual GitHub Actions workflow is included at `.github/workflows/staging-smoke.yml`. It runs `python -m app.staging_smoke` and requires all three repository settings:

- Repository variable `VELTRIX_STAGING_SMOKE_ENABLED=true`
- Repository variable `VELTRIX_STAGING_BASE_URL=https://<verified-staging-origin>`
- GitHub Actions secret `VERCEL_AUTOMATION_BYPASS_SECRET`

The bypass secret is sent only as the Vercel automation-protection request header from the GitHub runner. It must never be placed in Android BuildConfig, APK resources, source control, or chat. The workflow is manually dispatched and remains skipped until the enable variable is set. It checks liveness, database readiness, and the exact four-asset CoinGecko quote contract, including positive prices, provenance, timestamp timezone, five-minute freshness, and a 60-second future-skew limit. Unit tests cover the validators without making live requests.

Keep the database connection string only in the Vercel secret manager; it is not required by GitHub Actions.

## Security boundary and Android access

Vercel SSO protection is enabled for all deployment URLs. The backend currently exposes read-only health and market routes and has no account/session authentication layer. The Android Retrofit client does not implement Vercel SSO.

Do not disable SSO as a shortcut. Do not embed a Vercel protection-bypass token, API secret, database credential, or other shared server secret in the APK. The Android client needs a supported user-authentication path compatible with the protected staging ingress (for example, an OAuth 2.0/OIDC authorization-code flow with PKCE and server-side token validation, paired with an ingress configuration that accepts the resulting authenticated requests). This path is not implemented or verified yet.

## Release verification gates

1. Create the Vercel custom environment with slug `staging` for `veltrix-miner-staging`.
2. Provision a dedicated VELTRIX MINER staging PostgreSQL database; do not reuse `VELTRIXFOOTBALL`.
3. Configure `ENVIRONMENT=staging` and the dedicated `DATABASE_URL` as staging-scoped Vercel variables/secrets, not in Git or Android configuration.
4. Redeploy and verify `GET /api/v1/health/live` returns HTTP 200.
3. Verify `GET /api/v1/health/ready` returns HTTP 200 with `database=connected`; it must remain HTTP 503 otherwise.
4. Verify `GET /api/v1/market/quotes?assets=btc,xmr,ltc,doge` returns current provider-sourced USD quotes with source and retrieval timestamps. Provider failure must remain an explicit 503, never a fabricated quote.
5. Configure the GitHub Actions smoke-workflow variables and bypass secret, then dispatch the workflow and require a pass.
6. Keep deployment protection enabled and implement the supported Android user-authentication path without APK-embedded server secrets.
7. Configure Android with the verified HTTPS staging host and authentication flow.
8. Run an end-to-end contract check through the actual Android client against staging. Mocked tests and CI-only builds do not satisfy this gate.

## Current blockers

- A Vercel custom environment named `staging` has not been created.
- Dedicated VELTRIX MINER staging PostgreSQL database and connection string are not provisioned.
- The deployed readiness endpoint currently returns HTTP 503 because `DATABASE_URL` is absent.
- The Android client cannot authenticate through Vercel SSO; no secure app-access flow has been implemented.
- The live market endpoint responds with CoinGecko-sourced quotes, but the complete staging gate remains failed until database readiness and Android contract verification pass.
- The protected staging smoke workflow is implemented but not enabled/configured with its repository variables and automation-bypass secret.
- Do not build or distribute the device-test APK with a placeholder, guessed, unstable, or unverified API base URL.
