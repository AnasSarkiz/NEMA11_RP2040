# Reconstruction validation

Revision: `0.6.8-motor-assembly-wip`. Public baseline: `1233ccdf`.
The lost local placement and generated files were not recovered. All results
below must come from this revision's fresh runs. Older review records are
archived under `references/public-0.6.2-review/` and are historical only.

**Unrouted, untested prototype. Not fabrication-ready.**

## Motor assembly checkpoint

The separate native assembly wraps the unchanged electrical board with the
genuine OEM motor. Its 10 mm exploded viewing separation is not an approved
stack or spacer. Active USB placements remain adjacent; the opposite-edge
study rejects all recorded candidates and broader layout work remains open.
The complete motor model spans 28.2 × 48.2 mm in XY, failing the saved
28.3 × 28.3 mm whole-frame target. Excluding flexible leads still leaves a
31.2 mm main-solid wire-exit span, so that exclusion would not establish a pass.
No motor geometry is cropped. Hardware, mating, fasteners and insulation remain
unqualified. See [the motor review](docs/motor-assembly-review.md).

## Electrical verification state, 2026-11-10

The NEMA14 I2C0 pin allocation and seven functional sheets now have a fresh
native build. Electrical source, physical placement and supplier assets are unchanged.
The package now also includes the separate motor assembly and its validation. `checks/native-build-status.json` binds all native
inputs and the generated `dist/index/circuit.json` by SHA-256. The receipt
reports `fresh_output: true` and `build_passed: false`.

- Offline repository/source checks pass, including 48 prebuild regressions (14 for the motor assembly), plus eight
  root-selection tests and nine opposite-edge study tests.
- All 10 emitted contracts, 657 source/import assertions and independent
  conservative geometry checks pass.
- Native netlist reports zero errors/warnings. The current source check reports
  zero errors and five datasheet-service warnings (four timeouts and one HTTP 500);
  its strict gate fails. These are retained, not treated as a clean source pass.
- Pin semantics reports 30 warnings; its strict gate fails.
- Schematic analysis reports four findings: two imported label collisions,
  one cross-device decoupling grouping suggestion, and the bootstrap
  orientation diagnostic. Its strict gate fails. Findings are not waived.
- Native build exits 1 with two USB courtyard boundary errors, each 0.25 mm.
  There are no nested native errors. Placement analysis separately reports
  three courtyard collisions involving the optional encoder cluster and nine
  orientation suggestions. These are preserved for review, not dismissed by
  the separate native DRC result.
- 99 source/PCB components, 89 fitted CAD components (16 top, 73 bottom),
  67 source nets and 346 ports; zero PCB traces and vias.
- Seven A4 pages cover all 99 components and 346 schematic ports. Native PCB
  top/bottom views retain visible diagnostics. Crowded and off-board labels
  remain. Rendering/coverage is not detailed readability or assembly approval.
- `checks/milestone-status.json` is complete with `passed: false` and
  `manufacturing_approved: false`. Routing remains disabled.

The conservative geometry audit finds minimum copper gap 0.160 mm, edge gap
0.389003 mm and provisional R2.35 screw-head envelope gap 0.075 mm. These are
nominal estimates, not tolerance or mechanical-fit qualification.
See [the current native refresh report](docs/native-refresh-20261110.md).

| Stage                   | Status      | Remaining gate                                                                                                                     |
| ----------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Requirements            | blocked     | Full NEMA14 parity, all-top/upright USB fit and rear-bolt qualification remain incomplete.                                         |
| Schematic/BOM           | in progress | Four schematic findings, 30 pin warnings and live supplier qualification remain open.                                              |
| Placement               | blocked     | Two native USB boundary errors, three analyzer courtyard findings, orientations, artwork and mechanical qualification remain open. |
| Routing                 | not started | Disabled until prior gates pass.                                                                                                   |
| Automated/visual review | in progress | Fresh native evidence exists, but strict milestone gates fail.                                                                     |
| Fabrication             | not started | No approved CAM, assembly process or BOM/CPL.                                                                                      |
| Physical prototype      | not started | No physical measurements or approved fastening.                                                                                    |
| Publication             | WIP only    | Existing GitHub and tscircuit package; publication receipts are separate from hardware approval.                                   |

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

Current source-bound motor evidence: [motor assembly checkpoint](docs/motor-assembly-checkpoint-20261110.md).
