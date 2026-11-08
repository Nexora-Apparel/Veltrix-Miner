# Phase 2.2 — Backend staging deployment

The API can be deployed as a Docker web service using the repository-root
`Dockerfile`. This file intentionally does not provision cloud resources or
create a database; select a host and PostgreSQL instance before deployment.

## Required runtime configuration

- `ENVIRONMENT=staging`
- `DATABASE_URL`: PostgreSQL SQLAlchemy URL using the psycopg driver,
  e.g. `postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE`
- `COINGECKO_BASE_URL=https://api.coingecko.com`
- `COINGECKO_API_KEY`: optional, supplied only through the host's secret manager

Never commit production/staging credentials or place them in the APK.

## Health verification

- Liveness: `GET /api/v1/health/live` must return HTTP 200.
- Readiness: `GET /api/v1/health/ready` must return HTTP 200 only after a real
  PostgreSQL `SELECT 1` succeeds. A 503 means staging is not ready.
- Market contract: `GET /api/v1/market/quotes?assets=btc,xmr,ltc,doge`
  must return provider-sourced USD quotes with source and retrieval timestamps.
  Provider failure must remain an explicit error, never a synthetic quote.

## Release sequence

1. Create a dedicated staging PostgreSQL database and store its URL in the
   deployment secret manager.
2. Build and deploy the repository-root Dockerfile to a managed container host.
3. Configure a real HTTPS custom or platform domain with certificate validation.
4. Verify liveness, database readiness, and the live market contract from an
   external client.
5. Add the HTTPS base URL to the Android build as
   `VELTRIX_API_BASE_URL`; do not embed API keys or database credentials.
6. Run Android contract and lifecycle tests against that endpoint before device
   testing.

## Security and limitations

- No wallet private keys, seed phrases, or signing credentials belong in this API.
- Do not enable financial actions or mining workers through this service.
- The current backend has no production authentication/session system. Keep the
  staging service restricted until authentication and authorization are implemented.
- No database schema migrations or persistent user-data tables are provisioned
  by this foundation.
- A successful container build is not proof of a healthy staging deployment.
