# Routed four-hole compact review

The **current PCB has been changed in place** to four provisionally Ø2.7 mm
mounting holes on the actual **23 mm motor-bolt pattern**, at X/Y = ±11.5 mm.
The head exclusions are radius 2.35 mm on every copper layer. There is no carrier.
Component placement and routing are being reworked around those holes.
[`mount-revision-status.json`](../artifacts/compact-six-layer/mount-revision-status.json)
identifies the changed source/board hashes and invalidated checks. Rear bolt
thread/length remain unverified; these are explicit provisional PCB clearances.

**The zero-error evidence described below belongs to the preceding 25 mm
electrical checkpoint, not the changed current board.** Its immutable source
and review artifacts are retained in Git at
[`399ffc3`](https://github.com/AnasSarkiz/NEMA11_RP2040/tree/399ffc34d70be4861b0224960d5a135c1c9d0d20).
Fresh current-board DRC, connectivity, CAM and assembly checks are required.

The current native PCB/motor assembly contains **77 genuine models and no
carrier**. Its [geometry/export check](../artifacts/compact-six-layer/current-assembly-geometry.json)
compares all fitted original STEP poses with the actual
[native GLB](../artifacts/compact-six-layer/development-assembly.glb).
This is a geometry check, not proof that the assembly can be clamped or fabricated.
The current native DRC has **121 errors and seven warnings**; none is waived.
Placement and routing must be corrected before new CAM/BOM/CPL are accepted.

The electrical source still contains 86 components and 326 physical pins,
including the documented DNP encoder. All 76 fitted components remain on top.
The complete buzzer circuit is the only user-authorized feature omission.
The 28 × 28 mm PCB outline remains inside the motor's 28.3 mm maximum frame.
NEMA14 remains an unchanged reference.

The revised bolt holes are Ø2.7 mm at X/Y = ±11.5 mm. This is a provisional
clearance envelope for a shank up to 2.5 mm, not an inferred rear M2.5 thread.
The original motor STEP establishes four nominal rear Ø4 mm bolt heads on those
axes. Head exclusions reserve Ø4.5 mm plus 0.10 mm radial allowance on all six
layers. Actual bolt shank/thread, grip length, engagement, torque, insulation
and final clamping arrangement require verification. The nominal 2 mm rear-body
gap in the 3D study is not a qualified spacer/hardware selection.

All new controller publications use revisions of the existing
[Compact_Prototype package](https://tscircuit.com/AnasSarkiz/NEMA11_RP2040_Compact_Prototype).
The published 0.4.1 revision contains the old 25 mm carrier-based layout and is
historical. It must not be used as the completed direct motor-bolt design.

Design checks remain mandatory: original supplier pad/model integrity, connected
schematic pins, all-top fitted assembly, native DRC, independent copper and
clearance checks, every-pin connectivity, shorts, CAM round-trip, assembly and
motor-bolt/harness fit. The crystal routes require short top-layer paths and
local ground returns. Via drills remain at least 0.30 mm and pads 0.45 mm.
Any retained terminal via-in-pad process requires IPC-4761 Type VII filled and
copper-capped construction with factory acceptance; it is not a clearance waiver.

The 20 kΩ / 10 kΩ divider and 0.24 Ω genuine 1/3 W shunts retain an ideal 1.1 V
VREF / 0.573 A peak setting. The motor is rated 0.67 A per phase. A4988 accuracy
is not guaranteed at the proposed low VREF, so current calibration and hot
motor/driver measurements remain required. New routing must receive a fresh
sense-resistance and trace/thermal screen.

Unresolved manufacturing requirements also include approved six-layer 90 Ω USB
stackup and pair routing, maximum supplier/placement tolerances, bulk-capacitor
ripple and regeneration, the JST mating plug and wire termination inside the
frame, through-hole assembly acceptance, stock confirmation and physical bring-up.
The genuine OEM wire stubs remain untrimmed in CAD and extend beyond the frame.
The two original GCT STEP compounds still fail the supplier-solid validity check.
These findings are reported rather than replaced by invented models.

This revision is **not fabrication-ready**. Historical zero-error checks,
Gerbers and exact review BOM/CPL remain available at the immutable commit linked
above. Their old hashes do not validate the changed current board.

Rebuild the current source and assembly using the managed toolchain:

```sh
bun scripts/build-controller.tsx --compact --four-mounts --motor-bolts \
  --no-buzzer --layers 6 --placement config/compact-routing-placement.json \
  --out artifacts/compact-six-layer
bun scripts/build-controller-assembly.tsx
bun scripts/export-core-3d.tsx --compact --assembly --folder artifacts/compact-six-layer
/workspace/.venvs/nema11-cad/bin/python scripts/verify_direct_motor_assembly.py
```

The source build deliberately fails while native footprint conflicts remain.
Board routing must be regenerated from the source before rebuilding its assembly.
