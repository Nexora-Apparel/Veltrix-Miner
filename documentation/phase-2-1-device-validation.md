# Phase 2.1 — Android Build and Device Validation

## Current automated result
- GitHub Actions workflow: Android debug build.
- Commit: 9f992f577be31728e9e6824333548ccd9287c53c
- Run: 42423412410
- Result: successful.
- Artifact: veltrix-miner-debug-apk
- Artifact size: 15,103,023 bytes.
- SHA-256: 7737b03c54fa772781d126f37846188f95fb516e1368293cc7c7626712f8374d
- Artifact expiry: 2027-02-05.

## Physical-device validation target
Realme 5 Pro, Android 11, 6GB RAM.

## Installation
1. Open the repository Actions page and select the successful Android debug build run.
2. Download the `veltrix-miner-debug-apk` artifact ZIP and extract `app-debug.apk`.
3. Transfer the APK to the target phone.
4. If Android blocks installation, enable the one-time install permission for the file manager/browser used to open the APK. Do not enable unrelated permissions.
5. Install and launch the app.

## Acceptance checklist
- [ ] APK installs without a package or parse error.
- [ ] App launches and remains open for at least two minutes.
- [ ] Home, Profit, Coins, Wallet and More navigation all open.
- [ ] Dashboard shows unavailable values where no live source exists; no fabricated balance, hashrate or earnings.
- [ ] Coin comparison renders BTC, XMR, LTC and DOGE without implying that the phone mines them profitably.
- [ ] Wallet screen does not request or store a seed phrase/private key.
- [ ] System health and battery percentage render without crashing.
- [ ] Rotate screen, background the app, then reopen; no crash or lost navigation state.
- [ ] No excessive heating during this UI-only test.
- [ ] Android 11 permissions are limited to what the app actually needs.

## Evidence required to close Phase 2.1
Record device model, Android version, install result, launch result, failed checklist items, and screenshots of any failure. A successful CI build alone does not close physical-device validation.

## Gate to Phase 2.2
Do not declare Phase 2.2 complete until Phase 2.1 has passed. Phase 2.2 is Live Backend Connectivity: authenticated HTTPS API client, typed API contracts, live market data with source timestamps and staleness handling, worker status API, persistent settings, wallet transaction verification, and dashboard refresh/error states.

## Security and integrity constraints
- Never enter a wallet seed phrase or private key into the app or backend.
- Do not treat a public wallet address as proof of ownership.
- Do not display estimates as confirmed payouts.
- Do not run sustained mining workloads on the phone.
