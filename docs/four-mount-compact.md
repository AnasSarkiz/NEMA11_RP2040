# Four mounting holes within the motor frame

> Superseded mounting proposal. The active requirement is
> [direct mounting using the motor bolts](direct-motor-bolts.md), whose nominal
> STEP axes are on a 23 mm square. This page describes the historical 25 mm
> carrier interface, which does not meet that requirement. No carrier or case
> is allowed in the current design.

The historical [routed six-layer checkpoint](compact-six-layer.md) retains all four
holes. Native DRC, independent copper, every-pin connectivity, Gerber raster
shorts and six-layer CAM checks report zero errors, opens and shorts. The
[A4 mounting comparison](../artifacts/requirements/mounting-review/four-mount-comparison.pdf)
separates the PCB interface from the motor front threads and shows why the
reference dimensions cannot be copied directly. Its
[verification record](../artifacts/requirements/mounting-review/verification.json)
is bound to the actual routed native PCB. These are nominal geometry checks;
carrier, hardware and maximum-tolerance qualification remain open.

The historical candidate uses four PCB holes, adapting the reference's four-corner
arrangement to the 28.3 mm maximum assembly frame. The reference's exact 26 mm
pitch, Ø3.2 mm holes and Ø6.4 mm head envelope exceed the available outline.
The candidate uses **25 mm pitch, Ø1.8 mm holes and Ø3.2 mm head exclusions** for
separate M1.6 carrier screws. Each hole retains 0.60 mm nominal laminate to the
28 mm PCB edge. Fastener and tool maximum dimensions still need qualification.

The verified motor attachment remains four front M2.5 threads at 23 ±0.15 mm
pitch, minimum depth 3.5 mm. There are no assumed rear threads or rear shaft.

Adding the lower two head envelopes conflicts with the old placement, including
the buzzer area. Under the user's explicit permission, the complete buzzer
circuit is omitted and GPIO16 is marked NC. All other features, including both
sense paths, PD/data USB, power monitoring, debug/test pads, RGB, temperature
and the optional DNP encoder, are compared against published NEMA14 v1.13.0.
The source contains 86 components and 326 physical pins; all 76 fitted parts are
on top. Supplier copper pads and models are unchanged.

[Current native source](../src/compact/six-layer-board.tsx),
[current six-page A4 schematic](../artifacts/compact-six-layer/schematic-a4.pdf),
[current native assembly GLB](../artifacts/compact-six-layer/development-assembly.glb),
[exact review Gerbers/BOM/CPL](../artifacts/compact-six-layer/manufacturing-review.zip),
[mount requirements](../config/compact-four-mounts.json) and
[carrier proposal evidence](../artifacts/requirements/four-mount-carrier-proposal.json)
are retained for review. The actual native GLB has 78 models; all supplier/motor/
carrier bounds match their original CAD within 0.05 mm. Tolerance and physical
qualification are separate release requirements; this checkpoint is not
fabrication-ready.

The earlier [four-layer source](../src/compact/four-mount-board.tsx),
[placement and source evidence](../artifacts/compact-four-mounts/README.md),
[A4 PDF](../artifacts/compact-four-mounts/schematic-a4.pdf) and
[native GLB](../artifacts/compact-four-mounts/development-assembly.glb) remain
the frozen, unrouted 0.3.0 placement checkpoint.

The four-piece carrier proposal permits each quarter to approach the motor
radially before PCB installation. Its narrow rails are not strength qualified.
The nominal OEM STEP corner relief is not guaranteed by the drawing. Neither
sampled CAD paths nor a final nonintersecting model proves a buildable product.

The checked routed native snapshot is published separately as
[NEMA11_RP2040_Compact_Prototype 0.4.1](https://tscircuit.com/AnasSarkiz/NEMA11_RP2040_Compact_Prototype).
Version 0.4.1 adds this mounting review while preserving every native
circuit/PCB/3D record from 0.4.0.
All seven required remote files were independently downloaded and matched
byte-for-byte; the [publication receipt](../artifacts/publication/compact-prototype-0.4.1.json)
records the incomplete CLI upload and successful authenticated archive recovery.
Version 0.3.0 remains the historical unrouted release. Neither is a fabrication
release.

[Routing construction and layer-validation evidence](compact-routing-construction.md)
tracks development beyond the frozen 0.3.0 placement snapshot.
