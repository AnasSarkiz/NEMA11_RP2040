# Routed compact review checkpoint

**CURRENT PCB HOLE REVISION — placement/routing in progress.** The current board
now has four holes at X/Y = ±11.5 mm, matching the motor's nominal 23 mm square.
The provisional drill is Ø2.7 mm and each head exclusion has radius 2.35 mm.
These dimensions reserve a clearance envelope; the actual rear bolt thread and
length are not yet verified. Prior DRC/CAM/assembly records have the old board
hash and do not qualify this changed layout. See `mount-revision-status.json`.
See the
[direct-motor-bolt requirements](../../docs/direct-motor-bolts.md). Do not use the
carrier or order this PCB as the completed direct-mount controller.

The previous native tscircuit six-layer 28 × 28 mm PCB had four Ø1.8 mm holes at 25 mm pitch, 76 fitted parts on top, six A4 sheets and zero-error copper/connectivity/CAM checks. Its native PCB/motor/carrier GLB is historical. The current source retains the electrical features and authorized buzzer omission while placement and routing are reworked for the actual motor-bolt pattern.

NOT FABRICATION READY. USB pair/stackup, direct motor bolts/tool access, maximum tolerances, full mating harness, bulk-capacitor ripple/regeneration, factory process/stock and physical current/thermal qualification remain unresolved. Seven source metadata warnings and two original GCT STEP validity errors remain reported.

See [the engineering review](../../docs/compact-six-layer.md) and [hash-bound milestone results](milestone-verification.json). The retained Gerbers/BOM/CPL and milestone-verification.json describe the historical 25 mm board, not this changed revision. Fresh exports and full checks are required.

Current native 3D: 77 original models, current PCB plus genuine OEM motor, aligned
23 mm bolt axes and no carrier. `current-assembly-geometry.json` verifies the
actual GLB bounds. Clamp hardware, final insulation and terminated wire routing
remain unqualified. Native DRC currently reports 121 errors and seven warnings;
no findings are filtered or waived.

Fresh independent checks on this current PCB report **350 copper/drill/head
errors and one open GND net (three islands)**, with zero foreign-net copper
shorts in the physical graph. The six connected A4 sheets pass schematic ERC.
None of these source-level passes qualifies the failing physical PCB.
