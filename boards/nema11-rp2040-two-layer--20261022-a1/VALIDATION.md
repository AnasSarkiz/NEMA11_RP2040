# Validation — upgraded tools, imports and schematic review

Revision: `0.6.2-issues-review-wip`; date: 2026-10-23 (Europe/Tirane).
Task: `nema11-rp2040-two-layer--20261022-a1`.
Import comparison baseline: Git `b96bc2b158cee0256459a1a03d8df38c7f5c18af`.
Original controller/reference baseline: `2a9fa01f4c5ee052f18ce4c3c719bab706a5de36`.

**Unrouted, untested WIP prototype. Not fabrication-ready.**
The supplied [validation policy](docs/user-validation-policy.md) governs this
revision. Imported definitions, symbols, footprints, pin maps and model poses
remain unmodified. Native generated circuit JSON is retained unchanged. No
six-layer routing, CAM or thermal result applies to this two-layer board.

| Stage                      | Status      | Evidence / blocker                                                                                                                                                                         |
| -------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1. Requirements            | blocked     | Full buzzer and two layers/top-bottom assembly retained. Rear case-bolt dimensions and motor-to-PCB gap unresolved.                                                                        |
| 2. Schematic/BOM           | blocked     | 47 fresh imports succeeded. C5815189 slot width mismatch, default C99269/C458749 label clearance, alternative C165948 qualification and complete datasheet/stock/mating review unresolved. |
| 3. Placement               | blocked     | 157 native board layout records, 31 pin-role warnings and 13 schematic-placement findings.                                                                                                 |
| 4. Routing                 | not started | Disabled; native output contains zero PCB traces and vias.                                                                                                                                 |
| 5. Automated/visual review | in progress | TypeScript, 587 structural assertions and source/schematic pin attachment checks pass. Six-sheet A4 PDF exported and visually reviewed for rendering; layout approval remains blocked.     |
| 6. Prototype fabrication   | not started | No approved Gerbers/drills, exact JLCPCB BOM/CPL, CAM or assembly acceptance.                                                                                                              |
| 7. Physical prototype      | not started | No physical fit, electrical or temperature test evidence.                                                                                                                                  |
| 8. Store release           | not started | Publication is a WIP review milestone, not an approved product.                                                                                                                            |

## Upgrade and issue review

Actual `tsci upgrade` succeeded: tscircuit 0.0.3005. Local exact pins and lockfile
are CLI 0.1.2401 / tscircuit 0.0.3005. All 47 unique JLCPCB parts were freshly
imported into isolated candidates; all 141 original TSX/OBJ/STEP outputs were
promoted unchanged. One source changed (excluded C5815189); all 94 model assets,
manufacturer identities, pin labels, passive values and electrical pad mappings
match the baseline, allowing a uniform footprint-origin translation.

The GCT drawing specifies one round Ø0.71 mm locator plus one horizontal
1.01 × 0.71 mm slot at 8 mm pitch. The earlier inward-pinched polygon is fixed,
but the new slot is approximately 1.51 × 0.71 mm. It still fails the manufacturer
comparison. Raw supplier access returned 403; importer-only responsibility is
not established. C5815189 stays excluded, without a local footprint patch.

The [issue catalog](docs/tscircuit-issues-20261023.md) includes native fixtures
and evidence for the slot discrepancy, first-sheet-only default SVG export,
default imported label clearance, zero exit despite schematic findings,
upgrader failure status handling and net-label connection metadata. It separates
current reproductions from historical failures and environment observations.
No upstream issue/comment/message was sent. Previous refresh evidence is
historical; current reports are in `checks/20261023/`.

## Commands and results

Commands run from this task directory with `node_modules/.bin` on PATH.
No ignore flags, suppressed findings, generated-JSON edits or snapshot acceptance.

| Command / check                                                              | Exit | Result                                                                           |
| ---------------------------------------------------------------------------- | ---- | -------------------------------------------------------------------------------- |
| `tsci upgrade`                                                               | 0    | Actual global upgrade succeeded.                                                 |
| `bun install --network-concurrency 1 --prefer-offline`                       | 0    | Local exact versions installed; integrity verification enabled.                  |
| `tsc --noEmit`                                                               | 0    | Native definitions compile.                                                      |
| `python3 scripts/audit_component_refresh.py --evidence-dir checks/20261023`  | 0    | 47 complete import comparisons; not BOM approval.                                |
| `python3 scripts/verify_source.py`                                           | 0    | 587 structural/import assertions; native failures reported separately.           |
| `tsci check netlist index.circuit.tsx`                                       | 0    | No reported findings or internal exception.                                      |
| `tsci check pin_specification index.circuit.tsx`                             | 0    | 31 unresolved semantic pin-role warnings.                                        |
| `tsci check source index.circuit.tsx`                                        | 0    | No reported findings or internal exception.                                      |
| `tsci check schematic-placement index.circuit.tsx`                           | 0    | 13 findings; zero exit does not mean acceptance.                                 |
| Strict post-check schematic report gate                                      | 1    | Findings retained; gate fails.                                                   |
| `tsci check placement index.circuit.tsx`                                     | 1    | Placement fails.                                                                 |
| `tsci build index.circuit.tsx --pcb-png --pcb-svgs --schematic-svgs`         | 1    | Native output generated with 157 error records.                                  |
| `python3 scripts/verify_schematic_ports.py`                                  | 0    | 296 attached source/schematic ports + 36 explicit NC; 29 metadata discrepancies. |
| Corrected USB locator comparison                                             | 1    | Slot width mismatch; native fixture build alone exits 0.                         |
| `node scripts/export_a4_schematics.mjs` / `python3 scripts/export_a4_pdf.py` | 0    | All six A4 sheets, 92 components / 332 ports covered.                            |

All five required source checks complete without the former internal autorouter
exception. Native board errors: 60 footprint overlaps, 56 courtyard overlaps,
29 placement, 10 pad clearance and 2 outside-board records. C_BULK extends
0.289 mm and D_STATUS 0.142 mm beyond native board bounds. These are board-design
failures, not established tscircuit bugs. Routing remains gated.

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

## Schematic review artifacts

The [six-page A4 landscape PDF](artifacts/20261023/NEMA11-schematics-A4-WIP.pdf)
embeds 300 dpi renders of unchanged native SVG sheets. Vector SVGs remain in
`artifacts/20261023/schematic/`. Page dimensions and coverage are independently
recorded in `checks/20261023/a4-pdf-export.json`; the contact sheet and MCU sheet
were visually inspected. The rejected Inkscape conversion had black-filled
symbols; resvg rendering resolves that conversion problem. Crowded labels and
13 native schematic findings remain; readability is not approved.

Source/net and schematic geometry checks find 296 correctly attached non-NC
ports and 36 explicitly unused ports. The 29 `is_connected: false` values are
metadata discrepancies at matching label anchors, not actual open pins. This
check does not prove absence of schematic shorts, correct datasheet mapping or
PCB connectivity. Native JSON is never patched to change those flags.

Main PCB remains crowded. There is no full 3D motor/plug/fastener interference
approval, zero-shorts claim, qualified CAM or physical hardware test evidence.

## Publication

Destination remains the public GitHub repository `AnasSarkiz/NEMA11_RP2040`
and the same public `AnasSarkiz/NEMA11_RP2040_Compact_Prototype` package.
Publish `0.6.2-issues-review-wip` to tscircuit first, then push matching source,
lockfile, review artifacts and exact native JSON to GitHub. A separate package
identity is not created. `checks/registry-verification.json` and
`checks/publication-status.json` record actual upload/visibility/hash results;
local generation or requesting a preview alone does not prove publication.

The previous `0.6.1-import-refresh-wip` publication was verified: 302 files
matched public registry bytes and GitHub native JSON matched. Its receipts are
retained under `checks/history/0.6.1-*`. This does not attest to the new revision.
