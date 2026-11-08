# VELTRIX MINER — Phase 0: Feasibility

**Status:** In progress — measurements required  
**Date:** 2026-11-08  
**Budget constraint:** ₦0 new spending  
**Device:** Realme 5 Pro, Snapdragon 712, 6 GB RAM, Android 11 (previously established; verify against device settings)

## Objective

Establish whether any already-owned, explicitly authorised compute, electricity, and internet resources can support genuine cryptocurrency mining without new spending, unsafe device operation, or misleading profitability claims.

Phase 0 is a gate. No mining workload is authorised by this document.

## 1. Known device baseline

Previously established:
- Realme 5 Pro
- Qualcomm Snapdragon 712
- 6 GB RAM
- Android 11
- Typical battery capacity 4,035 mAh (manufacturer specification)

Not yet measured:
- Actual free storage and storage health
- Battery health, cycle/age condition, swelling or abnormal discharge
- Battery temperature at idle and during ordinary use
- Ambient temperature at the intended operating location
- Available compute beyond the phone
- Electricity source, reliability, marginal cost and outage pattern
- Internet type, stability, latency, packet loss, data allowance and marginal cost

Official Realme product specifications: https://www.realme.com/global/realme-5-pro/specs

## 2. Thermal safety gate

Realme guidance identifies 0–35°C as the ideal operating environment and warns that charging above 45°C can degrade battery performance:
- https://www.realme.com/global/support/troubleshooting
- https://www.realme.com/mea-en/support/kw/doc/2134379

Project safeguards for any future controlled test:
- Record ambient and battery temperature separately.
- Do not mine while charging the phone.
- Do not test in direct sunlight, on bedding, or in an enclosed space.
- Project warning threshold: battery temperature >= 40°C.
- Project stop threshold: battery temperature >= 42°C.
- Stop immediately for swelling, unusual smell, thermal shutdown, extreme-to-touch heat, or unexpected instability.
- These project thresholds are conservative internal safeguards, not manufacturer-certified thermal limits.
- No sustained mining test on the Realme 5 Pro is permitted during Phase 0.

## 3. Electricity feasibility

Record:
- Source: grid / solar / generator / other.
- Whether power is already available for normal use or requires additional fuel/payment.
- Outage frequency and duration.
- Whether the resource is explicitly authorised for this use.
- Incremental electricity or fuel cost attributable to mining.

Daily phone charging does not establish that electricity is free or that surplus capacity exists. Unknown cost must remain UNKNOWN, not zero.

## 4. Internet feasibility

Record:
- Connection: Wi-Fi / mobile data / other.
- Provider and plan type (do not publish account identifiers).
- Measured download/upload speed.
- Latency to a candidate pool endpoint, jitter and packet loss.
- Data allowance, remaining data and marginal cost.
- Stability over a representative observation period.
- Whether continuous pool connectivity is practical.

A high download speed alone does not establish mining suitability. Sustained availability, latency, packet loss, and data cost matter more to a pool-connected worker.

## 5. No-spend test procedure

1. Inspect Android Settings for model, RAM (where exposed), Android version, storage capacity and free storage.
2. Inspect battery condition physically; do not use a visibly swollen or damaged device.
3. Record idle battery temperature and ambient temperature after the phone has rested, using an already-installed/free method.
4. Observe normal everyday use only; do not run a mining benchmark or stress test.
5. Run one existing free internet speed/latency test; avoid repeated tests that consume mobile data.
6. Record electricity source, outages and any incremental cost.
7. Inventory other already-owned compute devices only if the user confirms they exist and are authorised for this use.

No new app, subscription, API, cloud resource, hardware, deposit, or paid test is required.

## 6. Pass/fail criteria

Phase 0 can pass only if:
- At least one suitable, already-owned and authorised compute resource is identified.
- Its operating system, algorithm compatibility, power draw and cooling constraints are known.
- Safe operating temperatures can be maintained.
- Electricity and connectivity are available without violating the ₦0 incremental-spend constraint.
- Pool access and payout conditions can be evaluated without paid dependencies.
- A defensible net-profit calculation can be made with measured or explicitly sourced inputs.

If no suitable compute exists, the result is **NO-GO for live mining at present**. The control platform may continue in read-only research/monitoring mode, but it must not claim active mining.

## 7. Phase 0 checklist

- [x] Record previously established phone model, processor, RAM and Android version.
- [x] Define conservative thermal safeguards.
- [ ] Verify device specifications in Android Settings.
- [ ] Record battery condition and idle temperature.
- [ ] Record ambient temperature at the intended location.
- [ ] Identify electricity source, reliability and incremental cost.
- [ ] Measure internet speed, latency, stability and data cost.
- [ ] Inventory other existing authorised compute, if any.
- [ ] Produce a documented GO / NO-GO decision.

## Decision rule

No live mining worker, deployment, database spend, paid API, cloud compute, or sustained phone stress test is authorised until Phase 0 passes its relevant gates. The ₦0 constraint is absolute.
