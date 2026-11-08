# Phase 2 — Android Application

## Target
- Device baseline: Realme 5 Pro, Android 11, 6GB RAM.
- Native stack: Kotlin, Jetpack Compose, Material 3.
- Minimum Android version: API 26.
- Initial app version: 0.1.0.

## First-release sections
1. Dashboard
2. System health
3. Profitability overview
4. Coin comparison
5. Wallet tracking
6. Mining worker monitoring
7. Settings and security

## Data-integrity rules
- The initial UI is an interface scaffold; it is not connected to a mining pool, market-data provider, wallet or backend.
- No earnings, hashrate, pool shares or payouts may be fabricated.
- Unknown values render as unavailable, not zero or estimated income.
- Estimated rewards, pool-confirmed rewards and blockchain-confirmed payouts must remain separate.
- Wallet private keys must never be collected or stored.

## Device constraints
- The phone is the control and monitoring device, not a presumed profitable mining worker.
- Avoid sustained CPU mining workloads on the phone.
- Battery percentage is read from Android's BatteryManager.
- Temperature and detailed CPU telemetry are not claimed unless supported and verified on the target device.
- Background monitoring and notification permissions will be implemented in a later integration step.

## Build and verification
- Build with JDK 17 and Gradle 8.7.
- Android Gradle Plugin 8.5.2; Kotlin 1.9.24.
- Compile/target SDK 34; min SDK 26.
- Verify on Android 11 before declaring device compatibility.
- This repository scaffold has not yet been compiled or installed on a physical device.

## Next implementation tasks
1. Add automated UI and unit tests.
2. Add persistent settings and secure authentication.
3. Add backend API client and typed response models.
4. Add live market data with source timestamps and staleness checks.
5. Add pool and worker adapters only after provider selection.
6. Add wallet address and blockchain transaction verification.
7. Add physical-device battery, thermal and lifecycle testing.
