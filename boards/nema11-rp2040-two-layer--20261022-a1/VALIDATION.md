# Validation — two-layer NEMA11 with buzzer

Revision: `0.6.0-two-layer-buzzer-wip`; 2026-10-22.
Task: `nema11-rp2040-two-layer--20261022-a1`.
Reference commit: `2a9fa01f4c5ee052f18ce4c3c719bab706a5de36`.

**Unrouted prototype; not fabrication-ready or hardware-tested.** The supplied
[validation policy](docs/user-validation-policy.md) controls this revision.
No earlier six-layer DRC, CAM, routing or thermal result applies.

| Stage                          | Status      | Evidence / remaining work                                                                                                                                                                                     |
| ------------------------------ | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Requirements                | blocked     | Two copper layers and buzzer restored; rear case-bolt dimensions, engagement and bottom-component gap remain unknown.                                                                                         |
| 2. Schematic and BOM           | blocked     | 46 fresh selected JLCPCB imports, unchanged definitions/models. Replacement USB-C C165948 datasheet, stock, electrical ratings and mating geometry not approved.                                              |
| 3. Placement                   | blocked     | Four CLI checks exit 0 but log internal autorouter exceptions; acceptance remains blocked. Placement exits 1 with 155 findings.                                                                               |
| 4. Routing                     | not started | Explicitly disabled. No PCB traces or vias. Two-layer current, ground-return, USB stackup and thermal design remain required.                                                                                 |
| 5. Automated and visual checks | in progress | TypeScript and independent source-preservation/import-integrity audit pass. Native build exits 1; standalone check exceptions remain unresolved. Visual overview rejects placement and schematic readability. |
| 6. Fabrication                 | not started | No qualified Gerbers, drills, JLCPCB BOM/CPL, CAM or assembly approval.                                                                                                                                       |
| 7. Physical prototype          | not started | No physical measurements, assembly or powered tests.                                                                                                                                                          |
| 8. Store release               | not started | This publication is a WIP source checkpoint, not an approved product.                                                                                                                                         |

## Current evidence

The native output contains 92 source components, 332 physical ports, 64 nets,
six A4 schematic sheet records and 82 fitted component CAD references. The
fitted component split is 16 top / 66 bottom. Optional AS5600 and its two
capacitors remain DNP. Seven bare PCB test pads are board features.

`checks/source-integrity.json` verifies every selected supplier identity,
physical pin-to-net connection, passive value and all imported asset hashes.
It checks buzzer restoration, DNP status, two-layer outline and absence of routes.
It does not approve electrical operation, mechanical fit or manufacturing.

Native build: 60 footprint overlaps, 56 courtyard overlaps, 29 placement errors
and 10 pad-clearance errors. These are 155 placement findings. A further native
`pcb_autorouting_error` records skipped routing after those errors: 156 total
error records. Routing is disabled and no ignore flags were used.
Warnings remain in the native output and check logs; none are waived.
The four zero-exit standalone checks also log `ExpandEdgesToEmptySpaceSolver
bounds must be finite` / `AutorouterError` despite disabled PCB routing. They
report zero checked errors, but the internal exception prevents clean acceptance.
No routing was added to the native output. Additional checks against the untouched
native JSON avoid the source-render exception for supported subcommands: source
reports zero errors, pin specification reports 31 warnings, and schematic placement
reports label collisions and alignment issues despite exit 0. The netlist command
does not accept the JSON array as a component and exits 1. Logs and exits are
retained under `checks/native-json-*`. None of these results establishes a clean
schematic/ERC gate. This tooling failure needs diagnosis;
zero exit status alone is not treated as a complete pass.

Visual review of `dist/index/pcb.png` confirms dense overlaps and unreadable
silkscreen. `checks/schematic-overview.png` shows the first native A4 sheet;
labels cross nearby wires and text is too small for acceptance. The exported
SVG is not a completed, readable six-page A4 PDF. Native CAD references are
included, but motor/plug/fastener interference and imported model poses are
not approved. A remote preview build is not manufacturing validation.

## Imports, availability and assembly blockers

- Fresh C5815189 USB4145-03-0070-C import is excluded: it has only one locating
  NPTH, whereas the manufacturer drawing requires two Ø0.71 holes at 8 mm pitch.
  The original imported files and manufacturer PDF are preserved. No patch is used.
- C165948 TYPE-C-31-M-12 is an unmodified replacement candidate with two locating
  holes. That alone does not approve the footprint, ratings, model or plug fit.
  Exact supplier CLI searches returned no stock result for either USB part.
- Required buzzer C94598 MLT-5020 is restored with its complete transistor,
  flyback, gate, pulldown and decoupling circuit. Manufacturer specification:
  3 V rated waveform, 2–4 V operating range, 4 kHz ±200 Hz, 50% duty;
  maximum 100 mA at the specified 3 V test, not guaranteed at 3.3 V.
  Coil 12±3 Ω; 3.3 V / 9 Ω = 0.367 A is a conservative DC transient screen.
  Buzzer supply and driver qualification remain pending.
- Supplier CLI search on 2026-10-22 reported 58,895 C94598 units. This is a
  snapshot, not a reservation; other BOM availability is not approved.
- JST mating PHR-4/contact termination, pin order, lead exit and frame envelope
  require assembly review with genuine models and specified wire gauges.

## Motor mounting and current

Motor: STEPPERONLINE 11HS12-0674S, 0.67 A/phase, maximum 28.3 mm frame,
33 mm body. PCB is 28 × 28 mm. Four existing rear case-bolt axes are at
X/Y = ±11.5 mm, matching 23 mm square pitch. No carrier or invented rear shaft.
The front M2.5 threads do not establish the rear case-bolt thread or length.
PCB Ø2.7 holes and 2.35 mm head keepout radius are provisional. Actual shank,
head tolerance, grip length, engagement, torque, insulation and motor-to-PCB gap
are unresolved. Whole assembly fit, especially bottom parts, is not verified.

The retained nominal A4988 divider gives VREF = 1.1 V; with 0.24 Ω shunts,
Itrip = VREF/(8 Rsense) = 0.573 A. Each shunt dissipates at most approximately
0.079 W at this nominal current, or 0.108 W at 0.67 A. These calculations alone
do not qualify low-VREF accuracy, tolerances, driver losses or board temperatures.
Two-layer copper widths, thermal vias and exposed-pad cooling need a new review.
Minimum via drill/pad remain 0.30/0.45 mm. Signal width 0.16 mm, clearance
0.15 mm and board-edge clearance 0.25 mm are constraints, not measured compliance.

## Reproduction and publication

Toolchain: `@tscircuit/cli@0.1.2261`, `tscircuit@0.0.2764`, Bun 1.4.2,
TypeScript 5.9.3; task-local dependencies and cache. Run from this directory:

```sh
export PATH="$PWD/node_modules/.bin:$PATH"
tsc --noEmit
python3 scripts/verify_source.py
tsci check netlist index.circuit.tsx
tsci check pin_specification index.circuit.tsx
tsci check source index.circuit.tsx
tsci check schematic-placement index.circuit.tsx
tsci check placement index.circuit.tsx
tsci build index.circuit.tsx --pcb-png --pcb-svgs --schematic-svgs
```

Exact command exits are saved in `checks/`. Generated circuit JSON is untouched
native output. Publication goes first to the existing public
`AnasSarkiz/NEMA11_RP2040_Compact_Prototype` package, then the matching source
and review artifacts to GitHub. Publication receipts record remote verification.
No fabrication order is authorized or attempted.

## Publication result for this checkpoint

Native CLI created `0.6.0-two-layer-buzzer-wip` in the existing public package,
then exited 1 after reporting two STEP upload failures. Exact public downloads
verified 220 files, including current `index.circuit.tsx` and untouched native
`dist/index/circuit.json`. Verification is partial; 29 compared files remain
unverified or differ, and later check/report files have not all been uploaded.
The registry last reported `ready_to_build: false`; no new preview build or
3D assembly render is verified. The service marked the WIP version latest.

The cloud outbound proxy then failed across tscircuit and GitHub with HTTP 503,
`upstream connect error` / `remote connection failure`. This blocks upload
recovery, full remote verification and GitHub push. Authentication had succeeded
before this transport failure. No new token is requested. Raw CLI failure logs
remain private in ignored `.cache/publication/`, because library error dumps can
contain request headers. Sanitized receipts are in `checks/`.

Resume the **same** registry release through the official
`package_files/upload_archive` endpoint, then verify all files and request its
preview build. Do not run another ordinary push to create a replacement package
or silently bump around the partial release. Commit source and review artifacts
locally; push to the existing `main` when network access is restored.

Recovery was attempted through the official archive endpoint; its first request
failed HTTP 503 before uploading any recovery files. `git push origin main`
also failed HTTP 503. The implementation and artifacts are preserved in local
commit `f7485ac`; this commit has not reached GitHub. No new tscircuit package
identity was created. Both failures are transport failures, not token rejection.

## Required upstream-version resolution for C5815189

The user requires the missing USB4145 locating hole to be resolved through a
released tscircuit update and a fresh, unmodified JLCPCB import. No newer version
could be fetched: npm registry queries return HTTP 503. No dependency or board
source was changed. The baseline geometry screen fails with one locating hole;
see `checks/usb-locator-baseline.json`, `checks/tscircuit-upgrade-status.json` and
`docs/tscircuit-usb-import-release-gate.md`. A newer release is not yet confirmed
to fix either the supplier data or conversion. The alternate C165948 remains
unapproved WIP and is not presented as a repair of C5815189.

## Full refresh attempt requested by the user

Latest npm metadata verified CLI 0.1.2400 and tscircuit 0.0.3003. Installing them
failed twice on cloud HTTP 503 downloads, including a serial network retry.
The working manifest was restored. No new-release imports were completed;
47 unique parts are queued, including C5815189. All original imported files
remain unchanged. See `docs/import-refresh-20261022.md` and
`checks/import-refresh/status.json` for exact evidence and pending versions.
This attempt does not resolve or newly validate any component geometry.
