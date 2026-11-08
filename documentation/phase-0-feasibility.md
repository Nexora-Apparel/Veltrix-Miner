# VELTRIX MINER — Phase 0: Feasibility

**Status:** NO-GO for live mining with currently identified resources  
**Assessment date:** 2026-11-08  
**Budget constraint:** ₦0 new spending  
**Device:** Realme 5 Pro, Snapdragon 712, 6 GB RAM, Android 11 (previously established; device Settings verification still pending)

## Executive decision

The user's Phase 0 report confirms:
- Electricity: public grid.
- Internet: mobile data.
- Phone battery condition: reported normal.
- Other existing compute: none.
- Current phone battery temperature: not measured.

**Decision: NO-GO for live mining at present.** The only identified compute is the Realme 5 Pro. No evidence establishes that sustained on-device mining is safe or profitable, and there is no other authorised compute worker. Grid electricity reliability/cost and mobile-data allowance/marginal cost are also unverified.

The web control platform, read-only monitoring, research, and architecture work may continue at zero cost. Do not represent these activities as mining or earnings. This decision can be revisited only if suitable already-owned and authorised compute is identified and all cost/safety gates pass.

## Objective

Establish whether any already-owned, explicitly authorised compute, electricity, and internet resources can support genuine cryptocurrency mining without new spending, unsafe device operation, or misleading profitability claims.

No mining workload is authorised by this document.

## 1. Known device baseline

Previously established (verify against Android Settings):
- Realme 5 Pro
- Qualcomm Snapdragon 712
- 6 GB RAM
- Android 11
- Typical battery capacity 4,035 mAh (manufacturer specification)

User-reported battery condition: **normal**. This is a visual/subjective report, not a battery-health diagnostic.

Still unverified:
- Actual free storage and storage health
- Battery health, age/cycle condition and physical inspection
- Battery temperature at idle and during ordinary use
- Ambient temperature at intended location
- Any suitable compute beyond the phone (user reports none)
- Phone power draw under any proposed workload (no workload test authorised)

Official Realme product specifications: https://www.realme.com/global/realme-5-pro/specs

## 2. Thermal safety gate

Realme guidance identifies 0–35°C as the ideal operating environment and warns about charging above 45°C:
- https://www.realme.com/global/support/troubleshooting
- https://www.realme.com/mea-en/support/kw/doc/2134379

Project safeguards for any future controlled test:
- Record ambient and battery temperature separately.
- Do not mine while charging the phone.
- Do not test in direct sunlight, on bedding, or in an enclosed space.
- Project warning threshold: battery temperature >= 40°C.
- Project stop threshold: battery temperature >= 42°C.
- Stop immediately for swelling, unusual smell, thermal shutdown, extreme-to-touch heat, or unexpected instability.
- These are conservative internal safeguards, not manufacturer-certified thermal limits.
- No sustained mining test on the Realme 5 Pro is permitted during Phase 0.

Current battery temperature: **NOT MEASURED**. Thermal gate remains open.

## 3. Electricity feasibility

**User report:** Public grid.

Still required:
- Whether supply is reliable enough for the proposed worker.
- Outage frequency and duration.
- Whether the device would use existing normal-use power or cause incremental consumption.
- Whether electricity is metered/prepaid and the marginal cost attributable to mining.
- Confirmation that the electricity is authorised for this use.

Grid availability does not mean electricity is free. Unknown cost remains UNKNOWN, not zero.

## 4. Internet feasibility

**User report:** Mobile data.

Still required:
- Provider and plan type (do not publish account identifiers).
- Available/remaining data allowance.
- Measured download/upload speed.
- Latency to a candidate pool endpoint, jitter and packet loss.
- Connection stability and marginal cost of additional data.
- Whether sustained pool connectivity is practical without purchasing extra data.

A high download speed alone does not establish mining suitability. Sustained availability, latency, packet loss, and data cost matter.

## 5. Compute inventory

**User report:** No other existing compute devices.

Therefore, the Realme 5 Pro is the only currently identified compute resource. It is retained as a control/monitoring device, not approved as a mining worker. No cloud/serverless/browser workaround is accepted as a substitute for a persistent, authorised worker.

## 6. No-spend procedure

1. Inspect Android Settings for exact model, RAM (where exposed), Android version, storage capacity and free storage.
2. Inspect battery condition physically; do not use a visibly swollen or damaged device.
3. Record idle battery temperature and ambient temperature after the phone has rested, using an already-installed/free method.
4. Observe normal everyday use only; do not run a mining benchmark or stress test.
5. Run one existing free internet speed/latency test; avoid repeated tests that consume mobile data.
6. Record grid reliability and any incremental electricity cost.
7. Record mobile-data allowance and marginal cost.
8. Do not install paid software, buy data, add hardware, deposit funds, or provision paid cloud resources.

## 7. Pass/fail criteria

Phase 0 can pass only if:
- At least one suitable, already-owned and authorised compute resource is identified.
- Its OS, algorithm compatibility, power draw and cooling constraints are known.
- Safe operating temperatures can be maintained.
- Electricity and connectivity are available without violating the ₦0 incremental-spend constraint.
- Pool access and payout conditions can be evaluated without paid dependencies.
- A defensible net-profit calculation can be made with measured or explicitly sourced inputs.

**Current result: FAIL / NO-GO for live mining.** The identified compute inventory is insufficient to approve a worker; thermal conditions and marginal electricity/data costs remain unverified.

## 8. Phase 0 checklist

- [x] Record previously established phone model, processor, RAM and Android version (device Settings verification pending).
- [x] Define conservative thermal safeguards.
- [x] Record user-reported battery condition as normal.
- [x] Record electricity source as public grid.
- [x] Record internet connection as mobile data.
- [x] Record that no other existing compute is available.
- [ ] Verify device specifications and free storage in Android Settings.
- [ ] Record battery and ambient temperature.
- [ ] Establish grid reliability and incremental electricity cost.
- [ ] Establish mobile-data allowance, performance and marginal cost.
- [ ] Identify suitable authorised mining compute.
- [x] Issue current GO / NO-GO decision: **NO-GO for live mining**.

## Decision rule

No live mining worker, deployment, database spend, paid API, cloud compute, or sustained phone stress test is authorised until all relevant gates pass. The ₦0 constraint is absolute. Reassess only when the compute and cost facts materially change.
