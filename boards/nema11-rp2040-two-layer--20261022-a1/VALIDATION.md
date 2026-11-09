# Reconstruction validation

Revision: `0.6.7-reference-refactor-wip`. Public baseline: `1233ccdf`.
The lost local placement and generated files were not recovered. All results
below must come from this revision's fresh runs. Older review records are
archived under `references/public-0.6.2-review/` and are historical only.

**Unrouted, untested prototype. Not fabrication-ready.**

## Current verification state

The source refactor adds NEMA14 I2C0 pin allocation and seven functional sheets. No physical placement or supplier asset changed. Offline source consistency is checked separately from incomplete feature parity: `npm run verify:offline` must pass, while `npm run check:reference-complete` intentionally fails until the missing requirements are implemented. See [the current source-refactor report](docs/nema14-source-refactor-20261109.md).

The new electrical-locality pose is present in source, but main native
verification is incomplete pending approval for external validation traffic.
There is no current `dist/index/circuit.json` or fresh native receipt. Fresh offline results are recorded in `checks/20261109-reference-refactor/`; prior 25-test results are historical. Native-dependent checks have not
completed for these inputs; the current status file records that explicitly.

The isolated candidate was built separately with the unmodified toolchain:
two existing USB boundary errors and no nested native errors. Three supply-pad
distances improve, with the other 42 measured pairs unchanged; both reviewed
driver-cap ground-return bounds also improve. Nominal provisional head margin
is 0.075 mm, still not a tolerance qualification. J_MOTOR X changed from 3.9
to 3.874997 mm; the reviewed anchor reference and explicit regression test
record this placement change without changing motor holes or USB anchors.
See `references/electrical-placement-20261109/` and the new engineering review.

The runner now writes a fail-closed partial status before each stage so an
interrupted future run cannot leave an old success summary looking current.
The interruption regression invokes no native tool or external request.

Everything in the following checkpoint section is historical evidence for
`7da9556`, not verification of the current main placement. Existing review
images/PDF also belong to that checkpoint. No production tool patches are
installed.

| Stage                   | Status      | Current evidence / remaining gate                                                                                        |
| ----------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------ |
| Requirements            | blocked     | 28 mm, two layers, 0.67 A motor, buzzer retained. Rear bolt/grip/gap and full-assembly fit unverified.                   |
| Schematic/BOM           | in progress | Source/net contracts pass; untouched compact imports retained. Three schematic findings and 30 pin warnings remain.      |
| Placement               | blocked     | New placement has two USB courtyard boundary findings; electrical locality, artwork and full mechanical fit remain open. |
| Routing                 | not started | Disabled until all prior gates pass.                                                                                     |
| Automated/visual review | in progress | Current main native verification incomplete; historical evidence retained and clearly distinguished.                     |
| Fabrication             | not started | No approved CAM, stackup, panel, assembly process or BOM/CPL.                                                            |
| Physical prototype      | not started | No physical measurements or approved motor fastening.                                                                    |
| Release/publication     | blocked     | Explicit publication approval pending. No new GitHub or tscircuit revision published.                                    |

Exact C94598 manufacturer evidence is in the repository's reconstruction
record. The 2021 linked sheet supports 3.0 Vo-p rated and 2–4 Vo-p operation,
4 kHz ±200 Hz, 50% square wave, and 250 °C maximum reflow peak. It does not
resolve peak/RMS current, freewheel behavior, acoustics or thermal limits at
the candidate's actual waveform. Preserve the buzzer and clamp; bench tests
remain mandatory.

Current mechanical assumptions are provisional: X/Y ±11.5 mm motor case-bolt
axes, Ø2.7 mm holes, R2.35 mm head envelopes. Front M2.5 threads do not qualify
rear bolts. No carrier, approved gap, rear thread, grip, torque or insulation
has been established. JLCPCB body-to-edge and panel-rail requirements must be
checked against the actual overhanging connector/panel arrangement.

No findings are waived or suppressed. Imported component definitions and
native generated circuit JSON must not be patched.

## Historical verified checkpoint 7da9556, 2026-11-09 UTC

This checkpoint is new work, not recovered old placement. Main native JSON
SHA-256: `b93b921adc556e840dee2bc4acb0d4f2de8fe990ebf6b6a2638e4636379acf51`.
Source SHA-256: `864cd4929a056bd1c07dfc3345ce04ca563f01db223f340dbc6514da1fb1a045`.
The full-input receipt is `checks/native-build-status.json`; all included
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

Review artifacts and all failed gates are retained. No routing, fabrication
order, GitHub push, merge or tscircuit publication has occurred.
