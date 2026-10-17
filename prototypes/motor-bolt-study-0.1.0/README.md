# NEMA11 existing motor bolt study

The current requirement is a PCB mounted directly using the motor's existing
case-bolt locations, **without a custom carrier, case clamp or enclosure**.
This package contains only the genuine, unchanged STEPPERONLINE
11HS12-0674S motor in its original OEM coordinates. It adds no PCB, carrier,
rear shaft, new motor holes or invented replacement bolts.

The original STEP shows four rear bolt heads on a nominal **23 × 23 mm square**,
at X/Y = ±11.5 mm. Their modeled heads have nominal Ø4 mm cylindrical surfaces.
The front drawing's M2.5 threads do not specify the rear case-bolt thread or
length. Actual bolts, engagement, motor clamping, insulation/support and final
PCB hole/tool dimensions remain to be verified.

![OEM rear bolt view](https://raw.githubusercontent.com/AnasSarkiz/NEMA11_RP2040/6340609c023731fd8fd386c013211de180430be3/artifacts/requirements/direct-motor-bolts/OEM-rear-bolt-view.png)

The historical 25 mm carrier PCB is 1.414 mm off each actual motor bolt axis
and **fails** the direct-mount alignment check. Its zero-error electrical
checks do not qualify a new PCB layout.

[Native CLI motor GLB](https://github.com/AnasSarkiz/NEMA11_RP2040/blob/6340609c023731fd8fd386c013211de180430be3/artifacts/requirements/direct-motor-bolts/OEM-motor-native.glb) ·
[actual native 3D verification](https://github.com/AnasSarkiz/NEMA11_RP2040/blob/6340609c023731fd8fd386c013211de180430be3/artifacts/requirements/direct-motor-bolts/native-motor-study-verification.json) ·
[STEP bolt inspection](https://github.com/AnasSarkiz/NEMA11_RP2040/blob/6340609c023731fd8fd386c013211de180430be3/artifacts/requirements/direct-motor-bolts/nominal-step-bolt-audit.json) ·
[current mounting requirements](https://github.com/AnasSarkiz/NEMA11_RP2040/blob/6340609c023731fd8fd386c013211de180430be3/docs/direct-motor-bolts.md).

Native GLB bounds match the original STEP within 0.05 mm. Original lead stubs
and front shaft remain intact. This is a **mechanical-only inspection study**,
not a validated direct-mount PCB or fabrication release.
