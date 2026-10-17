# Direct mounting using the motor bolts

The active requirement is **four PCB mounting locations on the motor's existing
rear case-bolt axes, with no custom carrier, case clamp or enclosure**. This
supersedes the 25 mm pitch / M1.6 carrier proposal. That proposal and the
published 0.4.x assemblies are historical references, not the requested mount.

The unchanged original STEPPERONLINE STEP contains **four existing rear bolt
heads on a nominal 23 × 23 mm square**, at X/Y = ±11.5 mm. Their convex cylindrical
head surfaces have nominal Ø4 mm and Z = 29–30 mm in the OEM coordinates. These
are actual model features, not newly invented rear holes. No rear shaft is
assumed. The nominal rear body maximum is Z = 31.5 mm.

![Rear view generated from the unchanged OEM motor solid](../artifacts/requirements/direct-motor-bolts/OEM-rear-bolt-view.png)

The [CAD inspection](../artifacts/requirements/direct-motor-bolts/nominal-step-bolt-audit.json)
checks the original model hash, the four head axes and their convex surface
normals. It compares those axes against the actual routed electrical baseline:
each historical 25 mm PCB hole is **1.414 mm from its corresponding motor bolt
axis**. That PCB therefore fails the new direct-mount alignment check, despite
retaining its separately verified zero-error copper and connectivity.

The published drawing specifies **front M2.5 mounting threads**, at 23 ±0.15 mm
pitch and 3.5 mm minimum thread depth. It does **not** specify the rear case-bolt
thread, under-head length, engagement or torque. Equal nominal front/rear pitch
does not establish that the bolts have the same thread. The CAD's visible head
diameter does not establish a shank diameter, thread or maximum head tolerance.

The [direct mounting contract](../config/direct-motor-bolt-mounting.json) leaves
PCB hole diameter, maximum screw/tool exclusion and rear bolt specifications
unset until they are verified. An added PCB and any standard insulating spacers
consume bolt length. Original bolts must retain proper motor clamping and
engagement; correctly specified longer bolts may be needed. The recessed heads,
metal rear cover, PCB bottom copper, case temperature and mechanical support
also need an actual insulation/spacing design. There is no approved direct
assembly or orderable hardware selection yet.

Default controller preview now shows the **electrical PCB baseline only**.
Historical motor/carrier assembly rebuilding requires the explicit
`--historical-carrier` option, to prevent reintroducing it as the current mount.
The [native motor study](../examples/motor-bolt-study.circuit.tsx) contains only
the unchanged genuine OEM motor in its original coordinates. It does not show a
false completed attachment or add substitute bolt geometry.
The [actual native CLI GLB](../artifacts/requirements/direct-motor-bolts/OEM-motor-native.glb)
is checked against the unchanged STEP in the
[native study verification](../artifacts/requirements/direct-motor-bolts/native-motor-study-verification.json).
It contains one genuine motor model, with its original leads and front shaft;
there is no PCB or carrier in this mechanical-only study.

Reproduce the geometry inspection with the CAD environment:

```sh
/workspace/.venvs/nema11-cad/bin/python scripts/inspect_direct_motor_bolts.py
# This next check must currently fail: the historical PCB uses 25 mm pitch.
/workspace/.venvs/nema11-cad/bin/python scripts/inspect_direct_motor_bolts.py --require-compatible-pcb
```

The PCB requires placement and routing changes around the verified axes, then
fresh DRC, every-pin connectivity, shorts, CAM, BOM/CPL and complete native 3D
assembly checks. The old zero-error electrical results do not qualify a new
layout. This mounting redesign is **not fabrication-ready**.
