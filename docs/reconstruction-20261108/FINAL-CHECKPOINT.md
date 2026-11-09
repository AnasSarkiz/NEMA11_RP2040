# Reconstructed NEMA11 placement checkpoint, 2026-11-09 UTC

This is a new reconstruction in the existing NEMA11 project, not recovery of
the lost local commits and not a V2 board. No GitHub, tscircuit or fabrication
publication has occurred. The existing public project still shows older work.

## Fresh main-project result

The 28 × 28 × 1.6 mm two-layer candidate retains both adjacent-edge USB-C
connectors, A4988, RP2040, required buzzer and optional centered DNP encoder.
There are 99 source/PCB components and 89 fitted CAD components, with 16 top
and 73 bottom. Imported component definitions and models remain unmodified.
Routing is disabled, with zero traces/vias.

Native PCB findings decreased from 143 through 35 to **2**. Both remaining
findings are USB connector courtyards about 0.25 mm outside board edges. There
are no nested error records in the final native JSON. The findings are not
waived or hidden. The native build and placement gate remain failed.

- Format/typecheck: pass.
- Prebuild regressions: 23 pass.
- Emitted contracts: 9 pass.
- Source/import assertions: 657 pass.
- Source/netlist diagnostics: zero reported errors/warnings.
- Pin semantics: 30 warnings; strict gate fails despite native exit 0.
- Schematic: 3 findings; strict gate fails despite native exit 0.
- Complete-input freshness receipt: current, with unchanged inputs during run.
- Six A4 schematic pages and separate top/bottom diagnostic views exported.

Final native JSON SHA-256:
`b93b921adc556e840dee2bc4acb0d4f2de8fe990ebf6b6a2638e4636379acf51`.
Source SHA-256:
`864cd4929a056bd1c07dfc3345ce04ca563f01db223f340dbc6514da1fb1a045`.
Placement input SHA-256:
`12dec2b98b47ac4374a035228cdb47cd60c51bc75e20b78f09053ecaa7a90f83`.

All full-run logs and receipts are under the board's `checks/` directory.
`checks/20261108-reconstruction/final-full-run.txt` is the final run, while
`full-run.txt` and `historical-35-native-findings-expanded.json` retain the
earlier 35-finding checkpoint. Current authoritative detail is in
`checks/source-integrity.json`, `checks/milestone-status.json` and
`checks/native-build-status.json`.

## Geometry and appearance limits

A portable conservative bounding-box audit includes rotated SMT pad bounds,
plated-slot outer copper, polygon pads and DNP copper. Its eight new regression
tests prevent omission of those shapes. Nominal conservative minima are
0.160 mm between different-component same-layer copper, 0.361098 mm to the
board edge, and only 0.044548 mm to provisional R2.35 bolt-head envelopes.
The last figure is not a tolerance/fastener clearance approval.

Native top/bottom review images are in
`artifacts/20261108-reconstruction/pcb/`. Errors and warnings are enabled.
The views were inspected; labels are still crowded, overlap and sometimes
extend beyond the board. This is not the final NEMA14-style presentation.
The unchanged schematic sheet SVGs cover 99 components and 346 ports; the
new six-page A4 PDF remains review-only, not a detailed readability signoff.

Full motor/plug fit, bolt thread/grip/engagement, insulation, motor-side part
height, gap, encoder alignment, panel/rail treatment and exact assembly
processes remain unresolved. Clock, decoupling, buck hot-loop and driver-return
placement need review before routing. All-top assembly with two upright USB-C
is not demonstrated. Independent coil telemetry and other documented NEMA14
requirement gaps remain open.

## tscircuit diagnostic fix candidate

`tscircuit-bootstrap-fix-cli083/` preserves a generic topology-based candidate
for the actual CLI analyzer 0.0.83, exact upstream source provenance, complete
owner history, source archive, patch, 15 passing regression variants and a
focused typecheck. Its replay on the final board input removes only the
bootstrap orientation finding, leaving the two imported label findings
unchanged. It is not installed in the board's production dependencies, has
not passed the whole upstream suite, and has not been published.

## Reproduction and next gates

From the existing board directory, install the pinned dependencies, generate
source, format, then run `python3 scripts/run_milestone_checks.py` as described
in its README. A nonzero result is expected until the listed gates are fixed.
The complete-history bundle preserves source, diagnostics, models, portable
fixtures and reports, but does not include installed npm dependencies.

Next work is electrical placement review, real motor/connector/fastener
geometry qualification, upright/all-top feasibility, imported-symbol/pin
metadata issues, final artwork and assembly acceptance. Do not route, order,
publish or describe this failed-gate WIP as fabrication-ready.
