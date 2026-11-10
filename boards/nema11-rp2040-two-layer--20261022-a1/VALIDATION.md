# Reconstruction validation

Revision: `0.6.9-opposite-usb-wip`, continuing motor checkpoint `0be7261`.
The original lost local work was not recovered; this is the existing reconstructed
NEMA11 project. Historical evidence does not validate later revisions.

**Unrouted, untested prototype. Not fabrication-ready.**

## Opposite-side USB and motor checkpoint, 2026-11-10

Power USB J_PD is north at (0,8.65) mm, rotation 180°. Data USB J_DATA is south
at (3.8,-8.65) mm, rotation 0°. Forty-five component poses are coordinated,
including three test-pad access corrections. Supplier definitions and electrical
connections are unchanged. All 99 source components, 346 ports, 67 nets and
310 source-trace records match published `0be7261` exactly.

Both normal and assembly native outputs are fresh, with equal before/after
291-file input fingerprints. Both native builds exit 1, retaining the same two
USB courtyard boundary errors. The test-point accessibility error found during
the first trial is fixed by physical pad relocation, not a waiver.

- 70 prebuild tests, eight repository tests, 11 emitted contracts and 657
  source/import assertions pass. Source regeneration, TypeScript, formatting
  and the expanded independent geometry screen pass.
- Native netlist and the separate final source check report zero errors/warnings.
  The main build JSON still retains 19 datasheet-service timeout warnings from
  that earlier build pass; the assembly build has none. This service variability
  is not silently normalized or evidence of complete pin qualification.
- Pin check reports 30 warnings. Schematic analysis reports four findings:
  two imported label collisions, cross-device decoupling grouping and bootstrap
  orientation. Both strict gates fail; no finding is waived.
- Placement analysis reports three optional-encoder courtyard collisions and
  eight orientation suggestions. Its native DRC reports two USB boundary errors
  and one motor-connector direction warning. The genuine JST is top-entry, but
  its imported footprint lacks insertion-direction metadata and the tool infers
  horizontal insertion. The warning remains for a documented supplier/import fix.
- There are 99 source/PCB components, 89 fitted CAD components (16 top, 73 bottom),
  67 nets, 346 ports and zero PCB traces/vias. Routing stays disabled.
- Seven A4 schematic pages and diagnostic-enabled top/bottom PCB views are fresh.
  Rendering/coverage is not detailed readability or assembly-artwork approval.
- `checks/milestone-status.json` is complete with `passed: false` and
  `manufacturing_approved: false`.

The expanded screen includes all DNP copper, genuine locator NPTH holes,
actual full test pads, fitted courtyards, plated tabs, board edges and provisional
screw envelopes. Minimum nominal copper gap is 0.160 mm, copper/edge gap
0.350086 mm, other-part NPTH/copper gap 0.289923 mm and full test-pad/courtyard
gap 0.199981 mm. However, C_BUZZER/R_DM courtyards have only 0.001 mm separation,
R_PWR_LED/J_MOTOR tab/body only 0.010 mm, and the provisional R2.35 screw-head
envelope only 0.075 mm. These are not tolerance-qualified assembly margins.
The two USB courtyards still extend 0.250021 mm beyond the board; their genuine
model faces are nominally flush. No envelope is shrunk or exempted.

The assembly contains the unchanged OEM motor. All 4,078 electrical, schematic,
PCB and existing CAD records match the normal board exactly; diagnostics and
project metadata are separately reported. All 89 fitted CAD models were checked,
with no missing models. The minimum nominal vertical gap is 8.17 mm only in the
explicitly exploded view. The 10 mm PCB-to-motor viewing separation is not an
approved spacer or stack. The uncropped motor spans 28.2 × 48.2 mm; its main
solid alone spans 31.2 mm in Y. The saved 28.3 mm whole-frame target still fails.

Rear threads, replacement bolts, length/engagement, torque, insulation, actual
stack gap, harness, mated plugs, extraction/tool access, assembly tolerances and
thermal behavior remain unqualified. Electrical routing, ground return paths,
USB impedance, current sensing and bench tests remain open. The bulk positive
feed improves but its longer ground return needs routing review. All-top/upright
USB feasibility and full NEMA14 parity are not demonstrated.

See [the current checkpoint](docs/opposite-usb-checkpoint-20261110.md),
[the genuine motor review](docs/motor-assembly-review.md) and
[historical motor checkpoint 0.6.8](docs/motor-assembly-checkpoint-20261110.md).
GitHub/tscircuit publication is a separate WIP checkpoint, not hardware approval.

## Preserved buzzer and mounting requirements

C94598 manufacturer evidence remains in the reconstruction record. The linked
2021 sheet supports 3.0 Vo-p rated and 2–4 Vo-p operation, 4 kHz ±200 Hz, 50%
square wave and 250 °C maximum reflow peak. Peak/RMS current, freewheel behavior,
acoustics and thermal limits at the actual waveform require bench qualification.
The buzzer and clamp remain present.

Nominal motor case-bolt axes are X/Y ±11.5 mm, PCB holes Ø2.7 mm and provisional
head envelopes R2.35 mm. Front M2.5 threads do not qualify rear bolts. No carrier,
rear thread, approved gap, grip, torque or insulation is established. Actual JLCPCB
edge/panel-rail and connector-overhang arrangements remain unqualified.

No findings are waived. Imported components and native generated JSON are not patched.

## Historical verified checkpoint 7da9556, 2026-11-09 UTC

This historical checkpoint is available in Git commit `7da9556`; current files at the same paths belong to the 2026-11-10 refresh above. It is new work, not recovered old placement. Historical main native JSON
SHA-256: `b93b921adc556e840dee2bc4acb0d4f2de8fe990ebf6b6a2638e4636379acf51`.
Source SHA-256: `864cd4929a056bd1c07dfc3345ce04ca563f01db223f340dbc6514da1fb1a045`.
The historical full-input receipt was `checks/native-build-status.json`; all included
inputs remained unchanged during verification. The private backup is a
checkpoint of failed-gate WIP, not release or publication approval.

- Format and TypeScript passed.
- All 23 prebuild regression tests and all 9 emitted contracts passed.
- All 657 source/import integrity assertions passed: expected physical nets, genuine part
  identities, values and explicit NC ports were preserved.
- Native source and netlist checks: zero reported errors/warnings.
- Native pin check: exit 0 but 30 warnings; strict warning gate FAILS.
- Native schematic check: exit 0 but 3 findings; strict gate FAILS. These are
  two untouched imported label collisions and the bootstrap orientation
  diagnostic. A separately tested upstream candidate is not installed.
- Native build and placement checks FAIL. Two top-level outside-board errors
  remain: J_PD and J_DATA courtyards extend about 0.25 mm beyond their edges.
  There are no nested error records and no reported footprint, courtyard
  overlap, pad clearance, copper-edge or bolt-keepout errors. No boundary
  exemption or diagnostic suppression is used. The earlier 35-error report,
  including eight nested pad failures, is historical evidence only and is
  preserved as `historical-35-native-findings-expanded.json`.
- 99 source/PCB components, 89 fitted CAD components (16 top, 73 bottom),
  67 source nets, 346 source ports, zero PCB traces/vias.
- Six native A4 pages exported successfully, covering all 99 components and
  346 schematic ports. The contact sheet was visually inspected for page
  rendering/coverage. This is not detailed schematic readability approval.
  Conversion observations embedded in the inherited PDF-export script refer
  to historical 2026-10-23 attempts, not new failed conversions in this run.
- Native layer-specific top and bottom SVG/PNG exports were generated with
  errors/warnings enabled and visually inspected. Silkscreen labels remain
  crowded, overlapping and in some cases beyond board edges. This is not
  the final neat presentation or assembly artwork.

The fresh layout improves 143 to 2 top-level PCB findings. Independent
conservative AABB analysis includes rotated SMT pills/rectangles, through-hole
outer copper, polygon pads and DNP copper. Minimum same-layer copper gap is
0.160 mm, copper-to-edge gap 0.361098 mm, and pad/courtyard-to-provisional
R2.35 bolt-head envelope gap only 0.044548 mm. Eight regressions cover these
geometry assumptions. These are nominal lower-bound estimates, not a
manufacturing-tolerance or mechanical-fit qualification. The tiny bolt margin
needs actual fastener/tolerance evidence, not an assumption of clearance.

Gate pulldown and gate resistor locality, the 7.84 mm MCU-to-crystal center
distance, decoupling, buck hot loop and driver-current returns still need an
electrical placement review before routing. Centers are not trace lengths.
USB mating, rear bolt grip/engagement, insulation, motor-side component height,
encoder alignment, PCB gap, panel rails and specific assembly processes remain
unqualified. All-top assembly with two upright USB-C is not demonstrated.

The separately preserved actual CLI analyzer 0.0.83 patch was replayed on this
exact native input. It reduces three findings to two by removing only the
ambiguous bootstrap orientation warning; both imported label findings are
unchanged. Its 15 regression variants pass. This patch is not installed in
the board's production dependency and is not a full upstream-suite approval.
The current strict schematic gate therefore still fails with three findings.

Stock warnings are not proof of zero inventory. One independent public C11702
lookup returned valid JSON with stock=null, whereas the official LCSC listing
reported stock. Complete live JLC assembly availability/quote is still open.

Review artifacts and all failed gates are retained. At that historical checkpoint, no routing, fabrication
order, GitHub push, merge or tscircuit publication had occurred. This sentence
does not describe the current publication state.

Current source-bound evidence: [opposite-side USB and motor checkpoint](docs/opposite-usb-checkpoint-20261110.md).
