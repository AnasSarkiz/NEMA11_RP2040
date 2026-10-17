# Four mounting holes within the motor frame

The current candidate uses four PCB holes, adapting the reference's four-corner
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

[Native source](../src/compact/four-mount-board.tsx),
[placement and source evidence](../artifacts/compact-four-mounts/README.md),
[six-page A4 PDF](../artifacts/compact-four-mounts/schematic-a4.pdf),
[mount requirements](../config/compact-four-mounts.json) and
[carrier proposal evidence](../artifacts/requirements/four-mount-carrier-proposal.json)
and [native assembly GLB](../artifacts/compact-four-mounts/development-assembly.glb)
are retained for review. The actual native GLB has 78 models; all supplier/motor/
carrier bounds match their original CAD within 0.05 mm. Routing, tolerance and physical qualification are
separate release requirements; this milestone is not fabrication-ready.

The four-piece carrier proposal permits each quarter to approach the motor
radially before PCB installation. Its narrow rails are not strength qualified.
The nominal OEM STEP corner relief is not guaranteed by the drawing. Neither
sampled CAD paths nor a final nonintersecting model proves a buildable product.

The checked native snapshot is published separately as
[NEMA11_RP2040_Compact_Prototype 0.3.0](https://tscircuit.com/AnasSarkiz/NEMA11_RP2040_Compact_Prototype).
The actual CLI upload exited successfully; all seven remote files were downloaded
and matched byte-for-byte. This publication is explicitly unrouted and does not
contain manufacturing-ready Gerbers/BOM/CPL.

[Routing construction and layer-validation evidence](compact-routing-construction.md)
tracks development beyond the frozen 0.3.0 placement snapshot.
