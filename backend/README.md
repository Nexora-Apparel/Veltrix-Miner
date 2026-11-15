# VELTRIX MINER API

Initial backend foundation for the web-first mining intelligence control plane. The service provides process liveness, database readiness and read-only market quotes. It does not expose mining controls, wallet signing, payouts, or fabricated mining/reward data.

## Local setup

Use Python 3.11 or newer.

```bash
cd backend
python -m venv .venv
# Activate the virtual environment for your operating system.
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The API listens on `http://127.0.0.1:8000`.

## Endpoints

- `GET /` — service metadata
- `GET /api/v1/health/live` — process liveness; does not imply database readiness
- `GET /api/v1/health/ready` — readiness; returns HTTP 503 unless the configured database responds to `SELECT 1`
- `GET /api/v1/market/quotes?assets=btc,xmr,ltc,doge` — CoinGecko USD quotes for supported assets; returns HTTP 503 on provider failure and includes retrieval timestamps/source provenance.

Market data is informational and is not used to calculate mining profitability. Provider timestamps represent retrieval time, not an exchange trade timestamp. Requests are capped at four supported assets. Configure `COINGECKO_API_KEY` only when using an authenticated CoinGecko Demo API plan.

## Web console CORS

Cross-origin browser access is disabled by default. To connect the static web console, set `WEB_ORIGIN` to its exact HTTPS origin, for example:

```env
WEB_ORIGIN=https://your-static-console.example
```

The backend accepts one origin only, permits GET requests and the `Accept` header, and does not enable credentialed CORS. Wildcards, insecure remote HTTP origins, paths, query strings and embedded credentials are rejected. For local development, HTTP is permitted only for localhost origins.

Set the web frontend's public `apiBaseUrl` in `web/config.js` to the API origin. This value is public configuration, not a secret. Never put API keys, database credentials, private keys or seed phrases in browser-delivered files.

A missing database URL is reported as `not_configured`. No placeholder database connection is treated as healthy. If readiness returns HTTP 503, the web console displays the database as unavailable rather than presenting it as connected.

## Tests

```bash
pytest
```

The CORS tests cover exact-origin allowlisting, rejection of unlisted origins, default-disabled CORS and invalid origin configuration.

## Security boundary

- Keep `.env` and real credentials out of Git.
- Do not place seed phrases, private keys or signing secrets in this service.
- Wallet integration is read-only by default.
- Do not interpret liveness as production readiness.
