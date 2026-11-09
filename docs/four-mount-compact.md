# Four mounting holes within the motor frame

> Superseded mounting proposal. The active requirement is
> [direct mounting using the motor bolts](direct-motor-bolts.md), whose nominal
> STEP axes are on a 23 mm square. This page describes the historical 25 mm
> carrier interface, which does not meet that requirement. No carrier or case
> is allowed in the current design.

The later six-layer variants were [removed](legacy-six-layer-removal.md).
The retained [A4 mounting comparison](../artifacts/requirements/mounting-review/four-mount-comparison.pdf)
and [verification record](../artifacts/requirements/mounting-review/verification.json)
are historical drawings bound to their original board hash, not validation of
the active two-layer board. Carrier, hardware and maximum-tolerance
qualification remain open.

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

The [mount requirements](../config/compact-four-mounts.json) and
[carrier proposal evidence](../artifacts/requirements/four-mount-carrier-proposal.json)
remain historical references. They are not fabrication-ready and do not apply
to the current direct-motor-bolt design.

The earlier [four-layer source](../src/compact/four-mount-board.tsx),
[placement and source evidence](../artifacts/compact-four-mounts/README.md),
[A4 PDF](../artifacts/compact-four-mounts/schematic-a4.pdf) and
[native GLB](../artifacts/compact-four-mounts/development-assembly.glb) remain
the frozen, unrouted 0.3.0 placement checkpoint.

The four-piece carrier proposal permits each quarter to approach the motor
radially before PCB installation. Its narrow rails are not strength qualified.
The nominal OEM STEP corner relief is not guaranteed by the drawing. Neither
sampled CAD paths nor a final nonintersecting model proves a buildable product.

The 0.3.0 four-layer source remains the historical unrouted release. Remote
registry versions were not changed by deleting the later six-layer design from
this checkout. None of these historical snapshots is a fabrication release.
