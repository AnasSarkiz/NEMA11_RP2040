# NEMA11 RP2040 controller

Hardware development for the STEPPERONLINE **11HS12-0674S**, to preserve the
published `AnasSarkiz/NEMA14_RP2040@1.13.0` feature set in a separate project.
The NEMA14 repository is a read-only reference.

**Active redesign target: the entire PCB and fitted connector/component bodies
must fit the motor's 28.3 ×28.3 mm maximum frame, with all fitted parts on top.
The existing routed 35 ×40 mm milestone below does not meet that new envelope.
[Compact redesign requirements and part candidates](docs/compact-controller.md).**

**The active four-hole candidate** has four corner mounting holes and removes
the buzzer circuit with the user's authorization. All 76 fitted parts are on
top; source, nominal placement and six connected A4 sheets pass.
[Four-hole geometry, evidence and remaining requirements](docs/four-mount-compact.md).
Routing and carrier qualification remain incomplete. Earlier two-hole compact
prototypes below are preserved historical checkpoints.

The default native preview opens the **four-hole 28 × 28 mm compact assembly**:
76 fitted parts on top, six connected A4 sheets and 78 checked native 3D models
including the OEM motor and proposed four-piece carrier. [Native GLB](artifacts/compact-four-mounts/development-assembly.glb).
This source/placement checkpoint is **unrouted**; full copper routing and carrier
qualification are in progress. The earlier two-hole compact escape prototype
has 58 disconnected nets, and the older zero-open routed baseline below uses a
larger outline. Those results do not qualify this four-hole candidate.

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

The new [28 mm compact placement milestone](docs/compact-controller.md) has native
[source](src/compact/board.tsx), [six A4 schematic sheets](artifacts/compact-controller/schematic-a4.pdf)
and [genuine-model 3D PCB](artifacts/compact-controller/development-controller.glb).
All 82 fitted parts are on top; nominal body fit and independent placement checks
pass. **Compact copper routing is in progress; this is not fabrication-ready.**

Published native compact development package:
[NEMA11_RP2040_Compact_Prototype](https://tscircuit.com/AnasSarkiz/NEMA11_RP2040_Compact_Prototype)
v0.3.0 — **four mounting holes, authorized buzzer removal, six connected A4
sheets and 78 native 3D models; UNROUTED, not manufacturing files**. The native
CLI upload succeeded and all seven registry files match locally byte-for-byte.
[Publication evidence](artifacts/publication/compact-prototype-0.3.0.json).
The v0.1.0 and v0.2.0 two-hole snapshots are preserved historical candidates.
