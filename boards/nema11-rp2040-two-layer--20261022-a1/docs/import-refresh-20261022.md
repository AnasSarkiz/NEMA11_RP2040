# Import refresh completed — 2026-10-22

`tsci upgrade` succeeded, installing tscircuit 0.0.3003 globally. The board's local
installation was then updated successfully to `@tscircuit/cli@0.1.2400` and
`tscircuit@0.0.3003`; exact pins and lockfile are committed. This supersedes the
earlier blocked attempts, retained in `checks/import-refresh/` as history.
The successful upgrade populated the default Bun package cache, which the
successful local installation reused. TLS and package integrity checks stayed on.

All **47 unique parts** were freshly imported using the supported command:

```sh
tscircuit-cli import --jlcpcb --download --use-exact-footprint C_PART_NUMBER
```

This includes all 46 selected BOM parts and the excluded C5815189 connector.
Every command exited 0 and returned original TSX, OBJ and STEP assets: 141 files.
The candidate outputs were copied byte-for-byte into `imports/`, without editing
component definitions, pins, symbols, footprint geometry or model poses.

The comparison against Git baseline `4775f9a` checks manufacturer identity, pin
labels, fixed passive values, electrical pad hints/dimensions/relative positions,
and model file hashes. All electrical comparisons match. Eight TSX definitions
changed; all 94 OBJ/STEP asset files are identical to their baseline. One CAD
origin changed, on the excluded C5815189. These checks do not approve datasheet
ratings, stock, complete mechanical fit or native model alignment.

## Blocking component finding: C5815189

The earlier description of two circular holes was incorrect. The GCT drawing,
page 2, specifies one Ø0.71 mm round hole and one **1.01 × 0.71 mm horizontal
slot**, at 8 mm spacing. Drawing tolerance is ±0.05 mm.

The new importer now includes the second opening as a polygon cutout, but:

- Its bounding dimensions are approximately **0.80 × 0.71 mm**.
- Its sides curve inward, leaving a narrow middle. Its area is approximately
  0.198 mm², versus 0.609 mm² for the nominal manufacturer capsule.
- It does not contain the minimum 0.96 × 0.66 mm capsule allowed by the drawing
  tolerance. Its locator center spacing is approximately 8.000 mm.

Thus the old missing-opening problem has changed into a malformed-opening
problem. The untouched new source and native diagnostic render reproduce it.
Do not patch it locally or approve this part. C5815189 remains excluded; the
board's C165948 alternative remains an unapproved candidate, not a repair of GCT.
The affected stages are schematic/BOM mechanical review, placement and assembly.

Evidence:

- `docs/GCT-USB4145-drawing.pdf`, page 2.
- `checks/import-refresh/usb-locator-new-cli.json` and `usb-locator-current.json`.
- `checks/import-refresh/usb-new-import.circuit.tsx`: native A4 review fixture.
- `dist/checks/import-refresh/usb-new-import/pcb.png` and `circuit.json`.

The native fixture builds successfully despite this defect. Build success alone
cannot establish that the imported geometry matches the manufacturer's drawing.

## Other findings and verification limits

- The former internal autorouter exceptions are absent in all five rerun CLI
  checks, with routing still disabled.
- Netlist and source checks report zero errors and zero warnings.
- Pin specification reports **31 warnings** about missing pin-role attributes.
  They remain unresolved; no imported definitions were edited to suppress them.
- Schematic-placement returns exit 0 while reporting label collisions, spacing
  and alignment issues. It is not accepted as a clean schematic-placement gate.
- Board placement and native build fail with **157 error records**: 60 footprint
  overlaps, 56 courtyard overlaps, 29 placement errors, 10 pad-clearance errors
  and two component-outside-board errors. The former skipped-routing error is
  absent. The two additional board-edge findings are C_BULK (0.289 mm) and
  D_STATUS (0.142 mm), measured against native component bounds.
- No PCB traces or vias are present. All 587 structural/import-integrity
  assertions pass. TypeScript passes with the refreshed imports.
- Installer peer warnings remain for circuit-json and circuit-to-svg; they are
  reported rather than treated as component failures or suppressed.
- Models were downloaded, but no complete 3D interference or manufacturer
  assembly approval is claimed. Stock is not reserved or verified for the BOM.

This revision is an **unrouted, untested WIP prototype**, not fabrication-ready.
