# VELTRIX MINER — Static web control centre

This directory contains the first web-first control-plane shell. It is plain HTML, CSS and JavaScript: no framework, package installation, paid service, database, API key or build step is required.

## Run locally

Open `index.html` in a browser, or serve the repository root with any local static file server and visit `/web/`. The interface is intentionally read-only.

## Current scope

- Responsive navigation for Overview, Market, Profitability, Workers, Pools, Earnings, Costs, Audit and Settings.
- Explicit `UNCONFIGURED`, `UNKNOWN` and `DISABLED` states.
- Static preview of Phase 0 NO-GO and Phase 1 implementation status.
- No fabricated prices, hashrate, worker count, balances, rewards or earnings.
- Refresh updates only the local view timestamp; it does not call an API.
- No browser mining, WebAssembly miner, background compute loop, wallet signing, private-key field or seed-phrase field.

## Integration boundary

The existing backend market endpoint is not connected to this page. Do not display live data until an API base URL, response schema, source timestamp, freshness policy and failure handling have been implemented and tested. Unknown data must remain unknown; missing costs must never be treated as zero.

Worker and pool controls are intentionally absent. Phase 0 currently blocks live mining because no separate compatible compute resource has been verified. A browser tab or serverless function is not a persistent mining worker.

## Validation

Run the dependency-free integrity suite from the repository root:

```bash
python -m unittest discover -s web/tests -v
```

GitHub Actions runs the same checks when web files change. These checks verify local assets, navigation/view consistency, required sections, responsive CSS and the absence of selected background-compute/polling primitives. They do not replace browser/device QA, accessibility testing, backend integration or production security review.
