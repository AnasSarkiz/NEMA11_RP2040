# NEMA11 RP2040 controller

Hardware development for the STEPPERONLINE **11HS12-0674S**, to preserve the
published `AnasSarkiz/NEMA14_RP2040@1.13.0` feature set in a separate project.
The NEMA14 repository is a read-only reference.

**Current mounting requirement: use the motor's four existing case-bolt axes
directly, with no custom carrier, case clamp or enclosure.** The unchanged OEM
STEP shows those rear axes on a nominal **23 mm square**. Rear bolt thread,
length and engagement are not specified in the front-thread drawing and remain
unverified. **The current PCB has been changed to four holes on the 23 mm square,
at X/Y = ±11.5 mm, provisionally Ø2.7 mm with larger head exclusions.** Placement
and routing are being reworked; prior DRC/CAM/assembly reports belong to the old
board hash and do not validate this revision.
[Current hole-change status](artifacts/compact-six-layer/mount-revision-status.json)
and [mounting requirements](docs/direct-motor-bolts.md).
The genuine motor-only inspection is published separately as
[NEMA11_RP2040_Motor_Bolt_Study 0.1.0](https://tscircuit.com/AnasSarkiz/NEMA11_RP2040_Motor_Bolt_Study).
Its native CLI upload succeeded and all seven files were independently
[downloaded and byte-verified](artifacts/publication/motor-bolt-study-0.1.0.json).
It contains the OEM motor only, with no claimed completed PCB attachment.

**Active redesign target: the entire PCB and fitted connector/component bodies
must fit the motor's 28.3 ×28.3 mm maximum frame, with all fitted parts on top.
The existing routed 35 ×40 mm milestone below does not meet that new envelope.
[Compact redesign requirements and part candidates](docs/compact-controller.md).**

**The previous electrical baseline was fully routed in native tscircuit.**
Its 28 × 28 mm six-layer PCB has four Ø1.8 mm corner holes at 25 mm pitch,
76 fitted parts on top, six connected A4 sheets and 78 native 3D models.
Native DRC, independent copper, every-pin connectivity, Gerber raster shorts
and six-layer CAM comparison report **zero errors / opens / shorts**.
The buzzer circuit is omitted with the user's authorization.
Its 25 mm mounting pattern is historical. Default preview now shows the current
23 mm hole revision of that same controller PCB together with the genuine OEM
motor: 77 native models, matching bolt axes and no carrier. New placement/routing checks are
required for this changed board.

[Current geometry revision, historical routed checks and unresolved requirements](docs/compact-six-layer.md).
[Native GLB](artifacts/compact-six-layer/development-assembly.glb).
This is a checked engineering prototype, **not fabrication-ready**: direct
motor-bolt layout/hardware, USB pair/stackup, maximum tolerances, harness, stock/factory acceptance
and physical electrical/thermal qualification remain open. Historical four-hole
0.3.0 and two-hole snapshots remain unchanged.

**Earlier 35 × 40 mm electrical baseline: full native controller source, six A4 sheets, routed copper,
review CAM, candidate SMT BOM/CPL and a native PCB/motor/front-carrier assembly.
Both manufacturer-required USB locating-hole corrections are complete. Native DRC reports zero errors with the documented exact-circle checker correction.
All 304 required pins on 92 components are physically connected; 37 intentional
NCs remain isolated. Independent copper, clock, USB ground-reference, shorts and
CAM checks pass.
This is not a fabrication release; [remaining requirements](docs/manufacturing-requirements.md)
include factory process/stackup acceptance, harness termination and physical qualification.**

Native CLI authentication now succeeds. The [separate MCU prototype](https://tscircuit.com/AnasSarkiz/NEMA11_RP2040_MCU_Prototype)
is published, and the exact NEMA14 v1.13.0 plus original motor drawing/STEP have
been retrieved. [Current source/access findings](docs/access-restored.md) include
verified motor ratings, source hashes and remaining integration requirements.

The [full controller prototype](https://tscircuit.com/AnasSarkiz/NEMA11_RP2040_Controller_Prototype)
is published as **0.3.0**, containing the routed PCB, six schematics, genuine OEM
motor and proposed front carrier. All seven required files were independently
downloaded and matched byte-for-byte. The registry preview build is pending;
the checked native GLBs below are available now. Immutable 0.1.0 and 0.2.0
source-only snapshots remain preserved. The native CLI upload encountered a
request-size limit; two separate unchanged-file archive uploads completed the
same release. [Publication evidence](artifacts/publication/controller-prototype-0.3.0.json)
records that recovery honestly.

- [Zero-error native DRC and every-pin connectivity](docs/native-drc-and-connectivity.md)
- [Design requirements](config/design-requirements.json)
- [Full controller PCB development and manufacturing blockers](docs/full-controller-pcb.md)
- [Factory process, harness and first-article requirements](docs/manufacturing-requirements.md)
- [Full controller source, parity and assembly findings](docs/full-controller.md)
- [Exact Gerber/BOM/CPL development review archive](artifacts/controller-pcb/manufacturing-review.zip)
- [Full controller six-page A4 schematic PDF](artifacts/controller/schematic-a4.pdf)
- [Full controller native PCB 3D review](artifacts/controller-pcb/development-pcb.glb)
- [Native PCB and OEM motor clearance arrangement](artifacts/controller/development-assembly.glb)
- [RP2040 subsystem source and verification](docs/rp2040-core.md)
- [Routed subsystem PCB, native 3D and checks](docs/rp2040-pcb.md)
- [Separate native tscircuit subsystem prototype source](prototypes/rp2040-core/)
- [Subsystem A4 schematic PDF](artifacts/rp2040-core/schematic-a4.pdf)
- [Engineering review and attachment constraints](docs/design-review.md)
- [Validation and release plan](docs/validation-plan.md)
- [Current-limit corner calculation](artifacts/requirements/current-budget.json)
- [Routed sense resistance, thermal and regeneration estimates](artifacts/requirements/routed-electrical-budget.json)
- [Observed v1.12.0 component/pin inventory](artifacts/requirements/reference-1.12-inspection.json)

Run the current milestone checks with:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/current_budget.py --output artifacts/requirements/current-budget.json
```

The subsystem build/check commands are documented in its review above. The
calculation tests validate design bounds, not operation of a physical motor.
Pending external prerequisites are documented in the engineering review. No
substitutions, fabricated rear holes or assumed rear shaft are authorized.

The historical [28 mm compact placement milestone](docs/compact-controller.md) has native
[source](src/compact/board.tsx), [six A4 schematic sheets](artifacts/compact-controller/schematic-a4.pdf)
and [genuine-model 3D PCB](artifacts/compact-controller/development-controller.glb).
All 82 fitted parts are on top; nominal body fit and independent placement checks
pass. That historical two-hole layout was not fully routed and is superseded by
the routed four-hole controller above.

Published native compact development package:
[NEMA11_RP2040_Compact_Prototype](https://tscircuit.com/AnasSarkiz/NEMA11_RP2040_Compact_Prototype)
v0.4.1 — **historical carrier-based six-layer compact review, four mounting holes, authorized
buzzer removal, six connected A4 sheets and 78 native 3D models**. Native DRC,
physical connectivity, shorts and CAM comparison report zero errors. All seven
required registry files were independently downloaded and byte-matched; large-file
CLI upload failures and recovery are recorded honestly in the
[publication evidence](artifacts/publication/compact-prototype-0.4.1.json).
The [A4 mounting comparison](artifacts/requirements/mounting-review/four-mount-comparison.pdf)
shows the PCB's four Ø1.8 mm holes at 25 mm pitch separately from the verified
motor front threads. Version 0.4.1 preserves every native circuit/PCB/3D record
from 0.4.0; it adds the mounting documentation.
**Not fabrication-ready**; see the current qualification requirements above.
Its carrier assembly is superseded by the direct motor-bolt requirement; this
published snapshot is retained as historical electrical/3D evidence only.
The v0.1.0 / v0.2.0 two-hole and v0.3.0 four-hole snapshots are preserved.
