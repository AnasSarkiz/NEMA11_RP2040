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

The retained native tscircuit controller has **zero native DRC errors, zero physical
opens, zero physical shorts and zero independent copper/clearance errors**.
Its 28 × 28 mm PCB has six copper layers and four Ø1.8 mm mounting holes at
25 mm pitch. All 76 fitted components are on top. The buzzer and its complete
drive circuit are the user-authorized omission; the other published NEMA14
v1.13.0 features and optional DNP encoder remain checked against that reference.
NEMA14 has not been modified.

The four PCB screws attach to a separate carrier proposal. The motor still has
only its verified front M2.5 threads, 23 ±0.15 mm pitch and 3.5 mm minimum tapped
depth. There are no assumed motor rear holes or rear shaft. Exact reference
Ø3.2 mm holes at 26 mm pitch extend outside the permitted frame, so the smaller
PCB hardware is a documented adaptation of its four-corner arrangement.
The [A4 mounting comparison](../artifacts/requirements/mounting-review/four-mount-comparison.pdf)
shows all three interfaces at the same scale: reference PCB, current PCB and
verified motor front threads. It is generated from the checked native mount
geometry and does not qualify carrier strength or manufacturing tolerances.

Current review outputs:

- [Native routed assembly](../artifacts/compact-six-layer/assembly.circuit.json)
  and [78-model native GLB](../artifacts/compact-six-layer/development-assembly.glb).
- [Six connected A4 schematic sheets](../artifacts/compact-six-layer/schematic-a4.pdf),
  326 physical pins, 290 required connections and 36 isolated intentional NCs.
- [Hash-bound check results](../artifacts/compact-six-layer/milestone-verification.json):
  all 61 nets physically connected; native CLI source, pin, netlist, schematic
  placement and Gerber raster short checks pass. Seven source metadata warnings
  remain visible in native DRC; none is a copper clearance or short waiver.
- [Gerbers and drill files](../artifacts/compact-six-layer/review-cam/), independently
  parsed against all six native copper layers, slots, holes, mask, stencil and
  outline. CAM reports zero errors; 281 drilled features are checked.
- [JLC SMT BOM](../artifacts/compact-six-layer/assembly-data/JLC_SMT_BOM.csv)
  and [CPL](../artifacts/compact-six-layer/assembly-data/JLC_SMT_CPL.csv): 75 SMT
  parts using genuine supplier R0 orientation data; one manual PH header is
  separate. CPL origin is the PCB lower-left, +14 mm from native X/Y. Three
  encoder DNP parts and seven bare PCB test pads are excluded.

Crystal signals remain on top, with no signal vias: XIN 2.40 mm, XOUT 2.30 mm
and XTAL_OUT 0.77 mm. Their local ground returns and inner1 reference are checked.
Via drills remain 0.30 mm; minimum pads remain 0.45 mm. The selected terminal
escapes require **IPC-4761 Type VII epoxy-filled, copper-capped vias** while
retaining the genuine supplier lands and their mask openings. Ordinary vias
remain prohibited in component lands. Factory process acceptance is pending.

The [new current/thermal screen](../artifacts/compact-six-layer/electrical-thermal-screen.json)
uses the actual compact routing. The 20 kΩ / 10 kΩ divider and 0.24 Ω shunts give
1.1 V VREF and 0.573 A ideal peak. Positive sense-path trace screens are 2.93 and
3.37 mΩ, corresponding to about 0.566 / 0.565 A nominal before ground-return,
switching and temperature effects. Both force paths stay on top; their terminal
vias are not counted as series barrels. The selected genuine shunts are 1/3 W;
each dissipates 0.108 W at the motor's full 0.67 A rating. With **35 µm finished
copper on every layer**, the largest legacy isolated-trace rise screen is
19.5 °C. This is not an IPC-2152 board thermal model.

The conditional 64-corner current upper screen is 0.658 A, but the A4988's
accuracy test conditions do not guarantee that bound at 1.1 V VREF. Current
calibration and hot motor/driver measurements are required. Conduction-only
driver loss is approximately 0.282 W at nominal sine-vector current, excluding
hot MOS resistance and switching/recirculation. The earlier oversized-board
sense-resistance results do not apply to this layout.

This checkpoint is **not a fabrication release**. Remaining requirements are
recorded explicitly:

- USB pair coupling, skew and an approved 90 Ω factory stackup require further
  routing review. Electrical continuity alone does not qualify USB operation.
- The four-piece carrier's narrow rails, genuine M1.6 hardware, tool access,
  fastener tolerances, torque, continuous assembly paths and vibration/strength
  are not qualified. The nominal motor STEP corner relief is not a guaranteed
  drawing tolerance. Its sampled collision-free insertion is a proposal.
- Nominal fitted bodies fit within 28.3 mm, but maximum supplier dimensions and
  placement/PCB tolerances are not verified. The bulk capacitor has little
  remaining nominal frame margin. Its ripple-current/ESR and bus regeneration
  also need qualification. The two original GCT USB STEP compounds fail the CAD
  validity check; those errors remain reported. Nominal solid collisions and
  connector lead/PCB fit checks pass.
- PH mating uses PHR-4 and SPH-002T-P0.5S contacts. Confirm the actual OEM AWG26
  insulation OD is 0.9–1.5 mm, crimp tooling, retention and the mating-view pin
  order: 1 A+ black, 2 A− green, 3 B+ red, 4 B− blue. Genuine complete plug,
  crimped wires and screw models are absent from the native assembly.
- JLC acceptance is needed for all-top assembly, USB shell through-hole soldering,
  the PH manual operation, filled/capped vias, 1 oz finished inner copper and
  controlled PCB maximum thickness compatible with the 1.6 mm PH limit. No stock
  reservation, assembly quote or first-article approval has been obtained.
- Phase current, maximum-ambient thermal operation, temperature shutdown
  calibration and bus overshoot under the actual load/stop profile need physical
  measurements. Motor leads leave toward the JST edge; their original STEP
  stubs are preserved and are not falsely trimmed to the PCB frame.

Rebuild the checked source and copper independently of the historical packages:

```sh
bun scripts/build-controller.tsx --compact --four-mounts --no-buzzer --layers 6 \
  --placement config/compact-routing-placement.json --out /tmp/nema11-six-source
cmp /tmp/nema11-six-source/unrouted.circuit.json artifacts/compact-six-layer/unrouted.circuit.json
python scripts/build_compact_six_layer.py --check
python scripts/verify_compact_six_layer.py
```

Use the repository's CAD Python environment for commands importing Shapely.
The immutable four-hole 0.3.0 package remains the earlier unrouted checkpoint.
