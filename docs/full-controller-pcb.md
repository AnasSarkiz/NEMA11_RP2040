# Full controller PCB review milestone

The native controller has all 92 reference components and 341 physical terminals
on a 35 × 40 mm, four-layer board. The active PCB and OEM motor/front-carrier
assembly are genuine tscircuit Circuit JSON. The default project opens the routed
assembly. This is a validated development milestone, **not a fabrication release**.
The immutable published 0.1.0 and 0.2.0 snapshots remain separate source milestones.

## Electrical and physical checks

The fixed PCB contains 554 traces, 334 vias, 46 anchored ground pours, 12 plated
component holes/slots and eight NPTH holes. Independent per-layer geometry checks
report zero opens, shorts, floating copper, clearance, drill, board-edge or circular
mounting-keepout errors. Minimum via drill/pad remain 0.30/0.45 mm. Three explicitly
reviewed ground vias sit in QFN exposed pads; they require the specified filled
and copper-capped process. All other via-in-pad findings are checked normally.

The native checker retains 36 errors caused by its rectangular approximation of
circular keepouts. The separate review matches every reported copper/keepout ID
and verifies clearance to its actual circle. Raw output is retained; the native
checker is not described as error-free. Nine supplier pin-metadata warnings also
remain visible. Independent connectivity does not rely on symbolic net membership
alone. Native Gerber shorts checks pass on all layers at 100 pixels/mm.

Every routed segment is checked against its electrical role and layer policy.
The four phase and two sense paths retain at least 0.30 mm copper. The A-minus
phase uses 10.5383 mm of inner-1 routing, including a bounded 6.6948 mm local
repair. The largest inner-1 ground region is 856.607 mm². Main 15 V distribution
uses wider copper; the reviewed ADC/TVS branch and short auxiliary necks have
separate current assumptions. The logic/data-input continuous budget is 0.5 A;
the shared PD design budget is 1.1 A. These are design budgets, not measured loads.

The crystal has no signal vias. XIN, XOUT and XTAL_OUT sections are 3.64, 4.80
and 2.68 mm, with nearby ground returns. USB coupled sections preserve reference
copper, 0.16 mm pair spacing and full-width adjacent ground coverage, with only
actual same-pair via antipad exceptions. This does not establish 90 Ω impedance:
a fabricator-approved stackup and impedance review remain necessary.

## Manufacturer corrections and native assembly

GCT drawing USB4145 A2, sheets 1–2, requires two 0.71 mm locating holes per USB
connector. The genuine import omitted the right hole. The project wrapper now
adds both missing holes without changing the supplier originals. Conflicting
15 V, STEP, DIR and phase routing has been repaired and rechecked. The original
USB model receives a +0.05 mm Z pose correction; the PH model receives its
verified +0.5500383 mm local Y correction. Neither model's geometry is altered.

Actual STEP sections check four shell stakes and two plastic pegs per USB, and
four PH leads, against the PCB holes. Nominal solid checks find no component-to-
component or component-to-laminate interference. OCCT flags the original GCT STEP
compound as invalid; that supplier-input limitation remains recorded. It has not
been silently healed or presented as a fully valid solid.

The routed native assembly and GLB contain 82 fitted supplier models, the unchanged
OEM motor and the original front carrier: 84 model bounds are independently
checked. Leads exit toward the JST edge. The maximum motor body leaves 8.2 mm
to the PCB bottom; the carrier uses documented front M2.5 threads only. Actual
fasteners, mating plug/contacts and the complete wire harness are still absent.
Conditional screw-head, tool and USB-plug envelope checks pass, subject to the
procurement limits in [manufacturing requirements](manufacturing-requirements.md).

## Exact review manufacturing files

`artifacts/controller-pcb/review-cam/` contains native Gerbers for four copper,
two mask, two paste and two silkscreen layers, fabrication/outline layers and
plated/nonplated drills. Independent Gerbonara parsing matches copper, paste and
all 354 drilled features to source within the stated 3 µm geometry comparison.
No silk overlaps mask openings; minimum actual silk-to-mask gap is 0.423 mm.
Minimum distinct top soldermask web is 0.1996 mm. Native mask apertures retain
the supplier geometry; factory mask compensation remains subject to approval.

The proposed 100 µm stencil has 319 apertures. Each of the three exposed pads
uses four windows totaling 60% coverage. All aperture aspect ratios exceed 1.5
and area ratios exceed 0.70. Plated holes, seven bare test pads and three optional
encoder DNP parts receive no paste. Functional silk uses 0.15 mm strokes; coil
order appears on the underside and pin 1 remains visible beside the PH header.

`assembly-data/JLC_SMT_BOM.csv` and `JLC_SMT_CPL.csv` contain the same 81 fitted
SMT designators in 44 exact supplier groups. The single PH header is in the
manual-assembly CSV. USB signal contacts are reflowed; shell stakes need the
factory's approved manual/selective solder operation. Genuine supplier R0 renders
provide the orientation metadata. The LED's original small pad skew has a
recorded pin-1 classification without changing copper. CPL origin is board
lower-left, in millimeters. No stock is reserved or JLC order submitted.

## Reproduction

Use the frozen Node toolchain and documented CAD/CAM Python environments:

```sh
npm run controller:build
npm run controller:check
python scripts/build_controller_pcb.py --check
bun scripts/check-controller-pcb.tsx --report-only
python scripts/audit_controller_pcb.py
python scripts/audit_core_clock.py --controller
python scripts/audit_controller_routing.py
python scripts/audit_controller_usb.py
python scripts/review_controller_native_drc.py
bun scripts/export-controller-review-cam.tsx
python scripts/audit_controller_cam.py
npm run controller:assembly
```

The source JSON plus fixed native connections reproduce this PCB byte-for-byte.
The grid router is construction history and is not needed for reproduction.
See the process, stock, harness and physical qualification requirements before
considering any fabrication release.
