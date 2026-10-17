# NEMA11 RP2040 MCU subsystem prototype

**Native tscircuit subsystem prototype. Not a complete motor controller and not
fabrication ready. This package describes the checked MCU-only development milestone.
See the GitHub publication receipt for the verified registry version and file hashes.**

`index.circuit.json` combines the checked routed MCU PCB, genuine supplier CAD
and three connected functional schematic sheets. It preserves the original
native board records and appends the verified schematic presentation. The
package deliberately has a separate name from the future complete controller.

Open this exact file with `tsci dev index.circuit.json`, or build it with
`tsci build index.circuit.json`. The full reproducible TSX source, supplier
imports, routing generator and independent checks are in the parent
[NEMA11_RP2040 GitHub repository](https://github.com/AnasSarkiz/NEMA11_RP2040).
`package-verification.json` identifies the committed input and scope.

The native PCB contains 31 source components: 24 purchased components and seven
bare debug pads. Internal copper connectivity, independent shorts/clearance,
clock layout, native schema, nominal supplier-solid collision checks and copper/
drill/paste CAM roundtrip pass within the documented subsystem scope. Native
DRC retains 15 external-interface opens and three crystal pin-attribute warnings.

The separate native 3D artifact is
[development-pcb.glb](../../artifacts/rp2040-pcb/development-pcb.glb); the
[A4 schematic PDF](../../artifacts/rp2040-core/schematic-a4.pdf) is also available.
These relative links resolve in the GitHub source tree; they are not promises
of registry-hosted files. Model URLs inside the native board are pinned to the
unchanged supplier data's immutable reference commit.

The final motor geometry/attachment, exact NEMA14 v1.13.0 source parity, CH224A,
power/data inputs, motor driver, accessories, encoder DNP, harness, complete
manufacturing BOM/CPL and production qualification remain outstanding. The
35 mm development outline has no motor mounting holes. Crowded silkscreen,
thermal-via fill/cap/stencil and nominal 0.075 mm via annulus still need review.

Registry access and native CLI authentication were verified on 2026-10-17.
The full motor controller remains incomplete, and no manufacturing release is
claimed by publishing this separate subsystem prototype. Supplier stock and
manufacturer tolerance qualification remain outstanding.
