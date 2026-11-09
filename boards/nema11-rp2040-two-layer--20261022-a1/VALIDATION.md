# Reconstruction validation

Revision: `0.6.6-reconstruction-wip`. Public baseline: `1233ccdf`.
The lost local placement and generated files were not recovered. All results
below must come from this revision's fresh runs. Older review records are
archived under `references/public-0.6.2-review/` and are historical only.

**Unrouted, untested prototype. Not fabrication-ready.**

| Stage                   | Status      | Current evidence / remaining gate                                                                               |
| ----------------------- | ----------- | --------------------------------------------------------------------------------------------------------------- |
| Requirements            | blocked     | 28 mm, two layers, 0.67 A motor, buzzer retained. Rear bolt/grip/gap and full-assembly fit unverified.          |
| Schematic/BOM           | in progress | Reconstructing compact PD/FET candidate with unchanged supplier imports. Fresh native electrical tests pending. |
| Placement               | blocked     | Known adjacent-edge connector anchors restored; full old placement unavailable. Fresh placement required.       |
| Routing                 | not started | Disabled until all prior gates pass.                                                                            |
| Automated/visual review | in progress | Fresh toolchain and fail-closed verification are being reconstructed.                                           |
| Fabrication             | not started | No approved CAM, stackup, panel, assembly process or BOM/CPL.                                                   |
| Physical prototype      | not started | No physical measurements or approved motor fastening.                                                           |
| Release/publication     | blocked     | Explicit publication approval pending. No new GitHub or tscircuit revision published.                           |

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

## Verified reconstruction checkpoint, 2026-11-09 UTC

This checkpoint is new work, not recovered old placement. Main native JSON
SHA-256: `056b8d48bb7fb60edcb96af118652b53589711eab4c5e885eff4c0b32db8ce91`.
Source SHA-256: `864cd4929a056bd1c07dfc3345ce04ca563f01db223f340dbc6514da1fb1a045`.
The full-input receipt is `checks/native-build-status.json`; all included
inputs remained unchanged during verification. The private backup is a
checkpoint of failed-gate WIP, not release or publication approval.

- Format and TypeScript passed.
- All 13 prebuild regression tests and all 9 emitted contracts passed.
- Source/import integrity passed: all expected physical nets, genuine part
  identities, values and explicit NC ports were preserved.
- Native source and netlist checks: zero reported errors/warnings.
- Native pin check: exit 0 but 30 warnings; strict warning gate FAILS.
- Native schematic check: exit 0 but 3 findings; strict gate FAILS. These are
  two untouched imported label collisions and the bootstrap orientation
  diagnostic. A separately tested upstream candidate is not installed.
- Native build and placement checks FAIL. There are 35 top-level PCB error
  groups: 8 footprint, 17 courtyard, 6 placement and 4 outside-board. Within
  those groups there are 25 related detail records, including 8 pad-clearance
  failures. Zero standalone pad-clearance records must not be mistaken for
  zero pad-clearance failures. See `native-findings-expanded.json` in the
  reconstruction check folder for exact counts and details.
- 99 source/PCB components, 89 fitted CAD components (16 top, 73 bottom),
  67 source nets, 346 source ports, zero PCB traces/vias.
- Six native A4 pages exported successfully, covering all 99 components and
  346 schematic ports. The contact sheet was visually inspected for page
  rendering/coverage. This is not detailed schematic readability approval.
  Conversion observations embedded in the inherited PDF-export script refer
  to historical 2026-10-23 attempts, not new failed conversions in this run.

The fresh layout improves 143 to 35 top-level PCB findings. Further targeted
placement remains in progress; nominal body/plug/motor/bolt clearance and
manufacturability remain unapproved. The fixed USB courtyards extend beyond
board edges and no off-board exemption is used. Some bottom passives still
conflict with connector through-hole geometry and provisional bolt keepouts.

Stock warnings are not proof of zero inventory. One independent public C11702
lookup returned valid JSON with stock=null, whereas the official LCSC listing
reported stock. Complete live JLC assembly availability/quote is still open.

Review artifacts and all failed gates are retained. No routing, fabrication
order, GitHub push, merge or tscircuit publication has occurred.
