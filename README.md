# VELTRIX MINER

Cryptocurrency mining intelligence and profitability platform.

## Android application — Phase 2

The first Android application scaffold is under `app/`.

### Requirements
- JDK 17
- Gradle 8.7
- Android SDK 34
- Android 11 or newer for the target device validation

### Build
```bash
gradle assembleDebug
```

The debug APK is generated at `app/build/outputs/apk/debug/app-debug.apk`.

### Initial screens
- Dashboard
- Profitability overview
- Coin comparison
- Wallet tracking
- System health and security

Worker monitoring is represented as an unconnected state until a real mining worker and pool provider are integrated.

### Data integrity
This is an application scaffold, not a live mining service. It does not fabricate balances, hashrate, rewards or payouts. Live market, pool, worker, wallet and backend integrations remain future tasks. The Realme 5 Pro is the control device, not presumed profitable mining hardware.

See [Phase 2 Android specification](documentation/phase-2-android.md).
