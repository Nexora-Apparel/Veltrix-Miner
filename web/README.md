# VELTRIX MINER — Static web control centre

This directory contains the first web-first control-plane shell. It is plain HTML, CSS and JavaScript modules: no framework, package installation, paid service, database or API key is required.

## Run locally

Open `index.html` through a local static file server (ES modules are not supported reliably from `file://`). The interface is read-only. For a same-device API integration, run the FastAPI service on localhost and configure its exact origin in `config.js`.

## API connection

1. Deploy or run the existing FastAPI backend.
2. Set `apiBaseUrl` in `web/config.js` to the API origin (for example `http://localhost:8000` for local development or an HTTPS origin for remote deployments).
3. For a cross-origin deployment, set backend `WEB_ORIGIN` to the exact static console origin. CORS is disabled unless this exact origin is configured.
4. Use **Refresh data** to make one bounded request to liveness, readiness and market endpoints. There is no automatic polling.

The frontend expects the existing contracts:
- `GET /api/v1/health/live` — status `alive`, service and version.
- `GET /api/v1/health/ready` — status `ready` and database `connected`; HTTP 503 is displayed as unavailable.
- `GET /api/v1/market/quotes?assets=btc,xmr,ltc,doge` — decimal-string USD prices, `coingecko` source and ISO retrieval timestamps.

The client validates schema, source, currency, positive decimal prices, all four requested assets and a maximum quote age of two minutes. It rejects unexpected future timestamps, invalid JSON, non-JSON responses, redirects, timeouts and failed HTTP responses. Remote API origins must use HTTPS. Browser requests omit credentials and do not store tokens.

Leave `apiBaseUrl` empty until a real backend origin exists. In that state the interface displays `UNCONFIGURED`; it does not invent data or retry in the background. Never place API keys, database credentials, private keys or seed phrases in browser-delivered files.

## Current scope

- Responsive navigation for Overview, Market, Profitability, Workers, Pools, Earnings, Costs, Audit and Settings.
- Explicit `UNCONFIGURED`, `UNKNOWN`, `STALE`, `VERIFIED` and `ERROR` states.
- Manual API health, database readiness and market refresh.
- No fabricated hashrate, workers, balances, rewards or earnings.
- No browser mining, WebAssembly miner, background compute loop, wallet signing or secret-entry fields.

## Validation

Run the dependency-free web integrity suite from the repository root:

```bash
python -m unittest discover -s web/tests -v
```

Backend tests:

```bash
cd backend
pytest
```

These tests do not replace browser/device QA, accessibility testing, production API deployment or live provider verification. No live API is configured in this branch.
