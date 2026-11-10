# NEMA11 exploded motor assembly review

`assembly-preview.circuit.tsx` wraps the actual current electrical board with the
unchanged STEPPERONLINE **11HS12-0674S, 0.67 A/phase** supplier model. Build this
entrypoint separately; the normal electrical entrypoint remains `index.circuit.tsx`.
Routing is still disabled. This is an **exploded review**, not an approved mounting
stack or fabrication release.

## Evidence and transforms

Package-local `references/motor-assets/11HS12-0674S.step` and `.obj` are byte-identical
copies of the repository's retained supplier STEP and its tessellation. SHA-256
values and manufacturer URL are locked in `config/motor-assembly.json`. Original
STEP inspection and mesh conversion provenance remain under repository-root
`artifacts/requirements/`. No generic NEMA model substitutes for the real motor.

The OEM model uses millimetres; front shaft points toward negative Z. Its rear
body maximum is Z=31.5 mm. The actual OEM rear bolt axes are X/Y=±11.5 mm;
retained inspection establishes recessed Ø4 mm heads, not a rear thread size.
The motor has zero rotation and translation (0,0,-42.3) mm. The PCB midplane
remains Z=0 with surfaces ±0.8 mm. Consequently the motor rear is at -10.8 mm,
**10 mm below the PCB bottom solely for exploded visualization**. This separation
is not a specified spacer or required operating clearance. All four nominal axes
remain aligned. The supplier wires and original bolts remain unchanged in the
motor mesh; they are not shown connected or fastening the PCB.

This follows the separate native assembly-entrypoint workflow in
[NEMA14 at d9fcd420](https://github.com/AnasSarkiz/NEMA14_RP2040_V2/blob/d9fcd4208bf7a93743447e1a0ab2c780aa08e304/assembly-preview.circuit.tsx).
NEMA14 dimensions, generic motor, proposed M3 screws, 6 mm spacers and harness
are deliberately not copied into this different motor design.

## Reproducible checks

Run `python3 scripts/check_motor_assembly.py` for the source contract. Unit tests
verify OEM hashes, axis alignment, origin/rotation/translation and exploded bounds.
After an authorized fresh native electrical build, run:

```sh
python3 scripts/check_motor_assembly.py --input dist/index/circuit.json \
  --output checks/motor-assembly-review.json
```

This rejects stale native poses. It reads each placed imported OBJ in its original
coordinates, subtracts the explicit native model origin, applies native Three.js
XYZ Euler rotation and translation, and reports source/world bounds, transform,
asset hash and conservative vertical separation from the entire OEM motor mesh.
A positive AABB separation proves only disjoint nominal meshes in this exploded
view. It does not validate an actual assembled stack, tolerances or thermal safety.
DNP parts are excluded from body checks but their copper still requires the normal
PCB audit. No exact solid intersection or tool-access qualification is claimed.

## Unresolved physical qualification

Rear thread/shank, under-head length, available engagement, case-clamping load,
torque, replacement-bolt choice, PCB support, real stack separation, electrical
insulation, bottom copper/solder clearance, case temperature, screw/tool access,
and motor-harness routing/connector mating remain unqualified. Four Ø2.7 PCB
holes and R2.35 head exclusions are provisional. The existing OEM bolts are recessed
below the rear cover and do **not** fasten this exploded PCB. No custom carrier,
enclosure, extra rear holes/shaft, replacement bolts or spacer geometry is invented.

## Native visual export

The installed CLI supports genuine native 3D PNG and GLB exports. After source
integration, the authorized native refresh can request:

```sh
node_modules/.bin/tsci build assembly-preview.circuit.tsx --3d-png --glbs
```

A nonzero build remains a failed gate even if diagnostic JSON/images are emitted.
Check the emitted motor CAD origin, zero rotation and Z=-42.3 translation against
the contract, and retain the native log/receipt. The normal PCB's mechanical audit
also requires the full-input native build receipt to be current; pose equality
alone is not sufficient. No preview from historical PCB output is a current result.

## Whole-frame requirement fails for unchanged OEM geometry

Fresh STEP solid inspection is recorded in
`references/motor-assets/oem-feature-inspection.json`. There are five solids:
four slender supplied lead stubs span Y=-34.1 to -14.1 mm (20 mm straight modeled
length), while the main motor/shaft solid spans X=±14.1 mm, Y=-17.1 to +14.1 mm,
and Z=-20 to +31.5 mm. The main solid includes a lateral feature at the wire exit,
approximately X=±6 mm, Y=-17.1 to -14.1 mm, Z=24.55 to 29.5 mm. Its material and
precise construction are not established by this geometry inspection.

The **uncropped complete motor is 28.2 × 48.2 mm in XY**, so it already fails
`whole_assembly_frame_maximum_mm = [28.3,28.3]` before adding the PCB and connectors.
Even removing lead stubs would leave the main solid's lateral feature with a
31.2 mm Y extent. Nothing is cropped or excluded from the actual assembly model.
The nominal 28.2 mm square motor body is not a whole-frame pass. Whether the
requirement should treat a flexible harness differently needs clarification;
real cable bending/routing and the rigid exit-feature envelope remain unresolved.
The 10 mm exploded Z separation does not resolve this XY incompatibility.

## Whole-assembly camera derivative

`node scripts/render_motor_assembly.mjs dist/assembly-preview/3d.glb OUTPUT.png`
reads the existing native GLB without changing geometry, computes world bounds
from all scene-node transforms/accessor bounds, fits a padded bounding sphere,
and uses installed PoppyGL to render a separate labeled 1200×1100 PNG. The adjacent
JSON records input/output hashes, complete bounds and explicit camera options.
The preliminary full-assembly image was visually checked: PCB, full motor body,
shaft and all four lead stubs fit within the frame. It does not replace the native
default image or qualify the preliminary placement.

Installed `circuit-json-to-gltf`'s `getBestCameraPosition` fits only the PCB/panel
rectangle at Y=0, without CAD model bounds. The default PNG pipeline supplies this
camera to PoppyGL. A local diagnostic confirmed identical camera results for the
entire native assembly and the PCB record alone. This is a general framing
limitation for tall/off-board assembly geometry, not evidence of wrong motor
transforms or missing motor mesh. PoppyGL's explicitly scene-fitted camera renders
the unchanged GLB fully. No upstream PR or dependency change was made.

To validate the actual emitted assembly as well as the source contract:

```sh
python3 scripts/check_motor_assembly.py --input dist/index/circuit.json \
  --assembly-input dist/assembly-preview/circuit.json \
  --output checks/motor-assembly-review.json
```

The extra input must contain exactly one OEM mechanical source, its genuine
package-local OBJ/STEP CAD record with the configured position, zero origin and
rotation, unit scale, and one linked quantity-one assembly BOM entry. After
removing those three expected additions, every electrical, schematic, PCB and
existing CAD record must match the index output exactly as a multiset. Additional
parts or changed netlist/geometry fail. Project metadata and diagnostic warnings/
errors are excluded from equality and their counts are reported separately;
mechanical equality does not waive native errors. The parent build workflow must
also retain its complete-input before/after receipt for the assembly output.
