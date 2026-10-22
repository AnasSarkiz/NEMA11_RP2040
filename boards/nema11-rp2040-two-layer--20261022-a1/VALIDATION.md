# Validation — upgraded imports, two-layer NEMA11 with buzzer

Revision: `0.6.1-import-refresh-wip`; date: 2026-10-22 (Europe/Tirane).
Task: `nema11-rp2040-two-layer--20261022-a1`.
Import comparison baseline: Git commit `4775f9a`.
Original controller/reference baseline: `2a9fa01f4c5ee052f18ce4c3c719bab706a5de36`.

**Unrouted, untested WIP prototype. Not fabrication-ready.**
The supplied [validation policy](docs/user-validation-policy.md) governs this
revision. No imported component, symbol, footprint, pin mapping or model pose
was manually patched. No six-layer routing, CAM or thermal result applies.

| Stage                      | Status      | Current evidence / blocker                                                                                                                                    |
| -------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Requirements            | blocked     | Two copper layers, top/bottom assembly and full buzzer retained. Actual rear case-bolt dimensions and motor-to-PCB gap unresolved.                            |
| 2. Schematic/BOM           | blocked     | All 47 fresh imports succeeded. C5815189 has a malformed locator cutout; C165948 alternative still needs datasheet, ratings, availability and mating review.  |
| 3. Placement               | blocked     | 157 native placement/clearance error records; pin-specification warnings and schematic-placement findings remain unresolved.                                  |
| 4. Routing                 | not started | Explicitly disabled; native output has zero PCB traces and vias.                                                                                              |
| 5. Automated/visual review | in progress | TypeScript and 587 structural/import-integrity assertions pass. Build exits 1. USB native fixture reproduces the malformed slot despite its successful build. |
| 6. Prototype fabrication   | not started | No approved Gerbers, drills, JLCPCB BOM/CPL, CAM or assembly acceptance.                                                                                      |
| 7. Physical prototype      | not started | No physical assembly, fit, electrical or temperature test evidence.                                                                                           |
| 8. Store release           | not started | Publication is a WIP review milestone, not an approved product.                                                                                               |

## Upgrade and full import refresh

`tsci upgrade` succeeded. Global and local tscircuit are 0.0.3003; the local CLI
is 0.1.2400. Package pins and Bun lockfile record the successful installation.
All 47 unique parts were freshly imported, including the 46 selected parts and
excluded C5815189. All returned original TSX, OBJ and STEP files. Their bytes
were promoted unchanged into `imports/`; none was patched.

All baseline manufacturer identities, pin labels, passive values and electrical
pad mappings match. Eight TSX definitions changed. All 94 model assets match
baseline bytes; only excluded C5815189's model origin changed. Full datasheet,
stock and 3D interference approval do not follow from those comparisons.

The C5815189 drawing requires one round Ø0.71 mm hole plus one horizontal
1.01 × 0.71 mm slot at 8 mm spacing. Earlier two-circle wording was incorrect.
The new importer produces an approximately 0.80 × 0.71 mm inward-pinched polygon
instead of the required slot. Native rendering reproduces it. Keep the part
excluded and stop dependent acceptance; no local geometry workaround is used.
See [the import refresh report](docs/import-refresh-20261022.md).

## Current commands and outcomes

Run from this task directory with `node_modules/.bin` on PATH. No ignore flags,
warning suppression, generated-JSON edits or forced snapshot acceptance used.

| Command                                                              | Exit | Interpretation                                                                           |
| -------------------------------------------------------------------- | ---- | ---------------------------------------------------------------------------------------- |
| `tsc --noEmit`                                                       | 0    | Refreshed definitions compile.                                                           |
| `python3 scripts/audit_component_refresh.py`                         | 0    | All 47 source/model comparisons completed; this is not BOM approval.                     |
| `python3 scripts/verify_source.py`                                   | 0    | 587 structural/import-integrity assertions pass; native errors reported separately.      |
| `tsci check netlist index.circuit.tsx`                               | 0    | Zero reported errors/warnings; no internal exception.                                    |
| `tsci check pin_specification index.circuit.tsx`                     | 0    | 31 unresolved pin-role warnings.                                                         |
| `tsci check source index.circuit.tsx`                                | 0    | Zero reported errors/warnings; no internal exception.                                    |
| `tsci check schematic-placement index.circuit.tsx`                   | 0    | Issues reported despite zero exit: label collisions and alignment/spacing. Not accepted. |
| `tsci check placement index.circuit.tsx`                             | 1    | Placement gate fails.                                                                    |
| `tsci build index.circuit.tsx --pcb-png --pcb-svgs --schematic-svgs` | 1    | Native output generated; 157 error records.                                              |
| Corrected USB locator screen on fresh C5815189                       | 1    | Manufacturer geometry mismatch.                                                          |

All five required CLI source checks now run without the former internal
autorouter exception. That earlier tooling failure is no longer reproduced.
The current native build reports 60 footprint overlaps, 56 courtyard overlaps,
29 placement errors, 10 pad-clearance errors and two outside-board errors.
The additional outside-board findings are C_BULK (0.289 mm) and D_STATUS
(0.142 mm), based on native component bounds. The former skipped-routing error
is absent. These board findings must be resolved; imported definitions are not
shrunk or patched to conceal them.

## Preserved controller and remaining engineering requirements

The native controller retains 92 source components, 332 physical ports, 64 nets,
six A4 schematic sheets and 82 fitted CAD references: 16 top, 66 bottom. Full
buzzer drive, two USB-C inputs, CH224A 15 V PD/POWER_GOOD, monitoring, RP2040,
flash/crystal/boot/debug, A4988, both shunts, microstepping, LEDs, temperature,
regulators/protection and JST motor connector remain present. AS5600 and two
encoder capacitors remain DNP. Seven bare test pads are native PCB features.

Motor: STEPPERONLINE 11HS12-0674S, 0.67 A/phase, maximum 28.3 mm frame and
33 mm body. PCB is 28 × 28 mm. Four existing rear case-bolt axes remain at
X/Y = ±11.5 mm (23 mm square). Ø2.7 mm holes and 2.35 mm head keepout radius
are provisional. Front M2.5 threads do not specify the rear bolts. Actual shank,
head, grip length, engagement, torque, insulation and bottom-part clearance
remain unverified. No carrier, invented rear thread or rear shaft is assumed.

Retained nominal current limit: VREF = 1.1 V, Rsense = 0.24 Ω,
Itrip = VREF/(8 Rsense) = 0.573 A. Shunt dissipation is approximately 0.079 W at
this current or 0.108 W at 0.67 A. Low-VREF accuracy, tolerance limits, motor-driver
losses and board temperatures still require qualification. Two-layer thermal
copper, ground return, USB stackup and power widths need review. Via minima remain
0.30 mm drill / 0.45 mm pad; 0.16 mm signal width, 0.15 mm clearance and 0.25 mm
board-edge clearance are constraints, not proof of measured compliance.

MLT-5020 C94598 buzzer and full transistor/flyback/decoupling stage are restored.
Datasheet rated waveform is 3 V, 4 kHz ±200 Hz, 50% duty; 100 mA applies at its
specified 3 V test, not as a guaranteed 3.3 V limit. The 3.3 V / 9 Ω = 0.367 A
DC transient screen and driver qualification remain pending. Prior supplier
snapshot reported 58,895 units on 2026-10-22; stock is not reserved and the full
BOM is not availability-approved. JST mating/termination, wire pin order and
whole-assembly frame clearance remain unverified.

Main PCB preview remains visually crowded. The USB fixture's native render shows
the inward-pinched locator cutout. Schematic readability and a complete six-page
A4 PDF remain unfinished. No full 3D motor/plug/fastener interference approval,
zero-shorts claim, qualified CAM or physical hardware testing is asserted.

## Publication

Destination remains the same public GitHub repository and the same public
`AnasSarkiz/NEMA11_RP2040_Compact_Prototype` package. This is a new version of
that existing package, not another package identity. Publish tscircuit first,
then push matching source, lockfile and native outputs to GitHub. Exact native
`dist/index/circuit.json` is included without editing. Remote receipts identify
completed uploads, hashes and visibility; do not infer success from local files
or a preview-build request. Earlier HTTP 503 attempts remain historical evidence.
