# NEMA11 RP2040 controller

The only active design is
[`boards/nema11-rp2040-two-layer--20261022-a1`](boards/nema11-rp2040-two-layer--20261022-a1/).
Root package entry, tscircuit preview and TypeScript configuration all select
that **two-layer** board. It is being refactored around the NEMA14 reference
requirements, with parts and mounting adapted to the smaller STEPPERONLINE
11HS12-0674S motor. The NEMA14 source remains a read-only reference.

**Work in progress, not fabrication-ready.** Routing stays disabled until
source, schematic and placement gates pass. Passing the offline checks below
is not a native schematic, placement, copper, CAM, thermal or hardware pass.
See the active board's [README](boards/nema11-rp2040-two-layer--20261022-a1/README.md)
and [validation status](boards/nema11-rp2040-two-layer--20261022-a1/VALIDATION.md)
for its current scope and blockers. Existing reports are tied to their original
inputs and do not validate subsequent source changes.

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
