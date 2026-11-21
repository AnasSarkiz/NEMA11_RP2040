# NEMA11 RP2040 controller

The only active design is
[`boards/nema11-rp2040-two-layer--20261022-a1`](boards/nema11-rp2040-two-layer--20261022-a1/).
Root package entry and TypeScript configuration select that **two-layer** board.
The tscircuit preview wraps the same board with its genuine OEM motor in a
separate, explicitly exploded assembly view. It is being refactored around the NEMA14 reference
requirements, with parts and mounting adapted to the smaller STEPPERONLINE
11HS12-0674S motor. The NEMA14 source remains a read-only reference.

**Work in progress, not fabrication-ready.** Routing stays disabled until
source, schematic and placement gates pass. Passing the offline checks below
is not a native schematic, placement, copper, CAM, thermal or hardware pass.
See the active board's [README](boards/nema11-rp2040-two-layer--20261022-a1/README.md)
and [validation status](boards/nema11-rp2040-two-layer--20261022-a1/VALIDATION.md)
for its current scope and blockers. Existing reports are tied to their original
inputs and do not validate subsequent source changes.

## Before enabling routing

The last checked-in native milestone is the November 10 opposite-side USB
checkpoint for `0.6.9-opposite-usb-wip`. The reports below describe that
source revision, not a fresh pass or a fabrication approval.

| Gate | Last checked-in result | What to verify next |
| --- | --- | --- |
| Pin specification | Strict check failed with 30 warnings. | Review the [pin report](boards/nema11-rp2040-two-layer--20261022-a1/checks/check-pin_specification.txt) against the exact fitted parts, then rerun the strict check. |
| Schematic placement | Strict check failed with four findings: two imported label collisions, cross-device decoupling grouping and bootstrap orientation. | Review all four in the [schematic report](boards/nema11-rp2040-two-layer--20261022-a1/checks/check-schematic-placement.txt) and rerun the strict check on the current source. |
| PCB placement | Native build and placement failed on the J_PD and J_DATA courtyard boundary errors. | Check the actual USB plug, overmold and panel/rail clearances against the [opposite-side geometry review](boards/nema11-rp2040-two-layer--20261022-a1/docs/opposite-usb-checkpoint-20261110.md). A nominally flush CAD model is not a mating or tolerance check. |

The [milestone record](boards/nema11-rp2040-two-layer--20261022-a1/checks/milestone-status.json)
records `passed: false` and `manufacturing_approved: false`. Keep routing
disabled while these gates remain open. Use the offline commands below for
source-only edits; when native checks are authorized, regenerate the evidence
from the exact current inputs rather than reusing these reports.

## Motor assembly and opposite-side USB request

Version **0.6.8-motor-assembly-wip** adds the genuine STEPPERONLINE motor to
[`assembly-preview.circuit.tsx`](boards/nema11-rp2040-two-layer--20261022-a1/assembly-preview.circuit.tsx),
following the NEMA14 separate-preview workflow. The **10 mm exploded gap is
only a viewing separation**, not an approved spacer or mounting stack. Rear
fasteners, engagement, insulation and mating remain unqualified. The unchanged
OEM leads extend the model to 28.2 × 48.2 mm; even the main solid's wire exit
exceeds the saved 28.3 mm whole-frame target. No geometry is cropped or hidden.
See the [motor assembly review](boards/nema11-rp2040-two-layer--20261022-a1/docs/motor-assembly-review.md).

**The new 0.6.9 floorplan places the power USB on the north edge and the data
USB on the south edge, offset 3.8 mm east.** The motor header moves to the east
and support components are coordinated on both layers. Earlier rejected trials
remain in the [historical search study](docs/engineering-review-20261110/opposite-usb/README.md).
The expanded audit includes actual USB locator holes, which revealed pre-existing
PD/support copper conflicts omitted by the older pad-only screen. Final native
results and remaining physical limits are recorded in the active board validation.

## Current all-top feasibility screen

The exact NEMA14 current-sensing parts and fitted encoder capacitors would
exceed the hypothetical upright-USB courtyard budget by **48.55 mm²** after
the provisional screw-head exclusions. This is a conservative area screen,
not proof that physical bodies cannot fit. No parts were added or removed
from the active board, and upright connector footprints still need qualification.
See the [reproducible area study](docs/engineering-review-20261110/all-top-parity-area/README.md).

## Earlier USB boundary investigation

The earlier adjacent-port connector errors concerned courtyards extending 0.250021 mm past the
board edge, while the outward copper remains 1.675871 mm inside it. Moving the
data connector inward just to clear that error would reduce two measured copper
gaps to about **0.035 mm**, below the required 0.15 mm. That study is pinned to the earlier adjacent-port placements. Connector mating,
assembly and tolerance evidence is still
needed before choosing a mechanical correction or any boundary exemption.
See the [pinned geometry audit and regression tests](docs/engineering-review-20261110/usb-edge-boundary/README.md).

## Current development

Install the active board's locked dependencies without lifecycle scripts:

```sh
npm ci --prefix boards/nema11-rp2040-two-layer--20261022-a1 --ignore-scripts --legacy-peer-deps --no-audit --no-fund
npm run verify:offline
```

Root commands forward to the active board:

- `npm test`: repository-selection regression and active prebuild tests.
- `npm run source:generate`: regenerate active source from its local inputs.
- `npm run source:check`: verify reproducibility without modifying source.
- `npm run check:contracts`: check the active source requirements.
- `npm run typecheck` and `npm run format:check`: local static checks.
- `npm run verify:offline`: repository and active-board offline source checks.

CI runs only the offline source checks and generated-source reproducibility.
It does not build/render native circuits, route, export CAM or publish packages.
Dependency installation can fetch packages, but the checks do not send board
source to a service. Native `build`/`dev` commands are manual entry points only;
native work that can contact a tscircuit service still needs the applicable
approval. See [development instructions](docs/development.md).

## Mounting and preserved references

The board must use the motor's existing rear case-bolt axes with no custom
carrier or enclosure. The nominal OEM STEP axes form a 23 mm square. Rear bolt
thread, length, engagement, tolerances, insulation and assembly clearance still
need qualification. See [direct motor mounting](docs/direct-motor-bolts.md).

The obsolete six-layer design, including `compact-current`, was deleted at the
user's request. It is no longer a build or preview default, and its old pass
reports must not be used to qualify the active design. The
[scoped deletion and recovery guide](docs/legacy-six-layer-removal.md) records
exactly what was removed and how to recover it from Git history.

Historical four-layer/MCU work, original supplier and OEM motor inputs, and
reference evidence remain available under `artifacts/`, `prototypes/`,
`imports/` and `references/`. They are historical evidence, not alternate active
boards. Remote registry history was not changed by this deletion.
