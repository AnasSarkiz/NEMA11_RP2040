# NEMA11 RP2040 — two-layer buzzer revision

Work in progress. This revision restores the required buzzer and changes the
PCB to two copper layers, with fitted components allowed on top and bottom.
It retains both USB-C inputs, CH224A 15 V PD and POWER_GOOD, RP2040/flash/clock,
A4988 and both current-sense paths, regulators/protection, LEDs, temperature,
debug/test points, JST motor connector and documented DNP encoder.

Source baseline: repository root controller at commit
`2a9fa01f4c5ee052f18ce4c3c719bab706a5de36`; mechanical/electrical artifacts in
`artifacts/compact-six-layer`. That six-layer revision and its generated files
are historical and are not modified by this task.

The intended PCB outline remains 28 × 28 mm inside the 28.3 mm maximum motor
frame, with four existing motor-bolt axes at X/Y = ±11.5 mm. Rear bolt dimensions,
clamping and space for bottom-side components are not verified. The former
Ø2.7 mm clearance holes are provisional, not verified rear M2.5 threads.

Follow [VALIDATION.md](VALIDATION.md) and the exact supplied
[validation policy](docs/user-validation-policy.md). Use only unmodified JLCPCB
imports. Native routing stays disabled until schematic, BOM and placement pass.
No current source or CAM is fabrication-ready or physically tested.

Destination: existing public `AnasSarkiz/NEMA11_RP2040` repository, `main` branch,
and existing `AnasSarkiz/NEMA11_RP2040_Compact_Prototype` package. Versions update
that same package; a separate registry package is not created for this task.

Current review revision: `0.6.2-issues-review-wip`. Actual `tsci upgrade`
succeeded; local pins are tscircuit 0.0.3005 / CLI 0.1.2401. All 47 unique
JLCPCB parts were freshly imported with untouched TSX/OBJ/STEP assets.
See [the tool/import issue report](docs/tscircuit-issues-20261023.md) for
reproductions, resolved behavior and remaining blockers. The GCT slot's pinching
is fixed, but it is 1.51 mm wide against a 1.01 mm drawing dimension.

The [complete six-sheet A4 PDF](artifacts/20261023/NEMA11-schematics-A4-WIP.pdf)
and unchanged vector SVGs cover all 92 components and 332 ports. Source and
schematic attachment checks pass for 296 connected pins plus 36 explicit NCs;
layout/readability approval remains blocked. There are 157 native board layout
records, 13 schematic findings and 31 pin-role warnings. Routing remains
disabled; no fabrication or physical test approval is claimed.
