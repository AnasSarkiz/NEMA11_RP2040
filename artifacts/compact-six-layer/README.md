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

NOT FABRICATION READY. USB pair/stackup, carrier/fasteners/tool access, maximum tolerances, full mating harness, bulk-capacitor ripple/regeneration, factory process/stock and physical current/thermal qualification remain unresolved. Seven source metadata warnings and two original GCT STEP validity errors remain reported.

See [the engineering review](../../docs/compact-six-layer.md) and [hash-bound milestone results](milestone-verification.json). Gerbers/BOM/CPL are exact review data, not an order release.
