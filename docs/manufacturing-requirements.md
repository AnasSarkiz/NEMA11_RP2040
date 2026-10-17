# Manufacturing and qualification requirements

The review Gerbers and exact candidate BOM/CPL are generated and checked. They
are not approved order files. No supplier quote, stock reservation, factory CAM
approval or assembled hardware test is represented by this milestone.

## Required PCB and assembly process

| Item | Required selection or unresolved acceptance |
| --- | --- |
| Outline | 35 × 40 mm; use the closed native outline and separate PTH/NPTH drills |
| Copper | Four layers, **1 oz finished copper on every layer**, including both inner layers |
| Thickness | Nominal 1.6 mm; obtain a controlled **1.60 mm maximum actual thickness** or written JST acceptance, because the PH catalog specifies 0.8–1.6 mm applicable PCB thickness |
| Finish/mask | ENIG, green mask; factory must review its registration/compensation against the supplied openings and 0.1996 mm minimum mask web |
| Vias | Minimum 0.45 mm pad / 0.30 mm drill; IPC-4761 Type VII epoxy filled and copper capped on vias only, including the three reviewed exposed-pad ground vias |
| Open holes | Do not fill component PTH/slots, USB locating NPTH or four mounting holes |
| USB locating holes | Four total 0.709981 mm nominal NPTH; manufacturer layout requires 0.71 ±0.05 mm. Obtain fabricator acceptance of finished tolerance |
| USB impedance | Preserve source copper until an approved four-layer stackup and 90 Ω differential calculation are reviewed. Current pair width/spacing and ground coverage alone do not prove impedance |
| Stencil | Candidate 100 µm; 60% four-window QFN exposed-pad coverage; factory approves paste, aperture release, reflow profile and filled-via plan |
| Assembly | 81 SMT placements; PH header and USB shell stakes need a separately quoted manual/selective operation |
| Panel | Factory panel rails, tooling holes, fiducials, placement polarity/origin and minimum-board handling require approval; no on-board fiducials are claimed |
| Parts | All 44 SMT supplier groups and the manual PH header need current stock/price/substitution review; no availability or genuine inventory guarantee follows from an import |

Published JLCPCB capability evidence is dated in
`artifacts/requirements/jlcpcb-published-capabilities.json`. Published nominal
capability is not board-specific factory acceptance. JLC's default half-ounce
inner copper does not meet this design's phase-path screen. Never submit the
older MCU-only subsystem Gerbers as a complete motor controller.

## Motor harness and physical assembly

Use the motor drawing's coil order: **1 A+ black, 2 A− green, 3 B+ red,
4 B− blue**. Header pin 1 is at PCB X=14.5 mm, with pins 2–4 progressing toward
X=8.5 mm. Confirm actual housing cavity numbering and mating-face view before
crimping. Check approximately 5.6 Ω ±10% per coil at 25 °C and no inter-coil
continuity, then verify assembled connector continuity; color alone is insufficient.

The genuine JST PH selection is B4B-PH-K-S(LF)(SN), PHR-4 housing and
SPH-002T-P0.5S contacts. The catalog accepts AWG30–24 but requires **0.9–1.5 mm
insulation outside diameter**. The OEM drawing specifies AWG26 UL1569 and does
not state outside diameter. Actual wire measurement or exact wire identity is
required; this question remains open. Obtain the applicable strip length, crimp
height, approved tool/applicator and pull-test criteria. Do not trim conductor
strands. Full lead trimming, bend radius, strain relief and a genuine mating
plug/contact model remain unverified. Only the OEM's original lead stubs are
shown in 3D.

The custom front carrier is a proposal, not a released machining drawing. It
uses four front M2.5 threads on 23 mm pitch; it invents no rear mounting holes or
shaft. Candidate front screws are M2.5×4 with purchased under-head length
3.7–4.1 mm and a 0.9–1.1 mm plate, giving 2.6–3.2 mm thread engagement below
the motor's 3.5 mm minimum depth. Candidate PCB screws are M2.5×5 with length
4.7–5.1 mm and 1.44–1.60 mm PCB, giving 3.1–3.66 mm engagement in 5 mm threads.
These are purchasing constraints, not verified screw specifications. A purchased
part must also meet maximum head diameter 4.5 mm, height 2.5 mm and the checked
2 mm hex-key access. Nominal envelopes pass; actual supplier CAD, front screw
access, tightening torque, retention and vibration testing remain required.

The USB cable overmold envelope is limited to 10 mm width ×8 mm depth. It clears
the nominal fitted component bounds. This is not an actual supplier cable model
or insertion test. The PH external housing envelope is a conditional clearance
screen, not verified crimp/contact insertion geometry. Machine-side mounting,
carrier machining tolerances, finish, thread inspection and thermal behavior
also need specification.

## Current, heat and first-article measurements

The 20 kΩ /10 kΩ divider and 0.24 Ω shunts give 1.1 V nominal VREF and
**0.572917 A ideal trip current** before routed sense resistance. A conditional
64-corner calculation reaches 0.657640 A, but its assumed ±5% driver allowance
is not a guaranteed A4988 accuracy bound at this VREF. The two actual sense
paths add approximately 16.66 and 18.62 mΩ at 20 °C under the stated 35 µm
copper/20 µm via-wall assumptions, reducing ideal trip estimates to 0.5357 and
0.5317 A. Ground offsets, switching inductance, real plating and shunt drift are
outside that estimate. Measure both coil currents at every microstep and verify
the motor current limit on hardware; rated holding torque is not established.

Each genuine 1/3 W shunt dissipates 107.7 mW at 0.67 A, 32.3% of its 70 °C
ambient rating. Its curve derates to zero at 155 °C. Driver conduction estimates
exclude hot resistance and switching loss; no junction temperature is claimed.
Measure motor, shunts, driver and PCB at 50 °C ambient, actual enclosure, stationary
holding and motion. Correlate TMP102 readings with the driver's local temperature.

The 18 V TVS is transient protection, not a qualified braking resistor. Its
published 200 W pulse rating assumes a specified pulse and manufacturer copper
layout. Regenerative bus rise depends on external inertia, speed, minimum effective
bulk capacitance and stop rate; those operating conditions are unspecified.
Verify bus overshoot and all component ratings during worst-case deceleration.
Also qualify 15 V PD negotiation, POWER_GOOD and both voltage ADC readings,
USB enumeration/data, boot/flash/SWD, all microstep controls, RGB/power LED,
buzzer, temperature sensing and the documented encoder DNP configuration.

Detailed assumptions and numerical results are in `current-budget.json` and
`routed-electrical-budget.json` under `artifacts/requirements/`. Physical results,
stock and vendor acceptance must be added before changing the release status.
