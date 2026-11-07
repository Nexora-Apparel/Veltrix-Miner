# VELTRIX MINER API

Initial Phase 2.2 backend foundation. This service currently provides liveness and database-readiness checks only. It does not expose mining controls, wallet signing, payouts, or fabricated market/reward data.

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

- `GET /` — service metadata
- `GET /api/v1/health/live` — process liveness; does not imply database readiness
- `GET /api/v1/health/ready` — readiness; returns HTTP 503 unless the configured database responds to `SELECT 1`
- `GET /api/v1/market/quotes?assets=btc,xmr,ltc,doge` — live CoinGecko USD quotes for supported assets; returns HTTP 503 on provider failure and includes retrieval timestamps/source provenance.

Market data is informational and is not yet used to calculate mining profitability. Provider timestamps represent retrieval time, not an exchange trade timestamp. Requests are capped at four supported assets. The provider is CoinGecko; configure `COINGECKO_API_KEY` when using an authenticated Demo API plan.

A missing database URL is reported as `not_configured`. No placeholder database connection is treated as healthy.

## Tests

```bash
pytest
```

## Security boundary

- Keep `.env` and real credentials out of Git.
- Do not place seed phrases, private keys, or signing secrets in this service.
- Wallet integration is read-only by default.
- Do not interpret liveness as production readiness.
