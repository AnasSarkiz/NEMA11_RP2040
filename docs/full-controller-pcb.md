# Full controller PCB development

The native routing milestone contains all 92 source components and 341 physical
terminals on a 35 × 40 mm, four-layer, nominal 1.6 mm board. It is not released
for fabrication. The published 0.2.0 prototype is the separate unrouted source
snapshot; this active routing is currently reviewed in GitHub.

The PCB has 547 traces, 339 vias, 46 anchored ground pours, 12 component plated
holes/slots and six NPTH holes. The independent geometry audit reports zero opens,
shorts, copper-clearance, drill-clearance, board-edge or circular mounting-keepout
errors. The native checker retains 36 rectangular approximations of circular
keepouts; each is independently checked against its actual circle. No other
native DRC errors remain. These raw results and their review are both retained.
Native Gerber shorts checks at 100 pixels/mm report no shorts.

The full native CAM output is in `artifacts/controller-pcb/review-cam/`.
Independent Gerbonara parsing matches all four copper layers, paste and 357
drilled features to the source, with no silkscreen over mask openings. These
files are explicitly development review output, not order data. The crowded
supplier silkscreen has been replaced by functional board and connector legends;
the genuine supplier copper and component models remain preserved.

The clock remains on top copper, with zero signal vias and short ground returns.
Its three routed sections measure 3.64, 4.80 and 2.68 mm. The native assembly GLB
includes 82 fitted supplier models, the unchanged OEM motor and the original
front carrier proposal; all 84 model bounds are independently verified. Carrier
nominal solid checks pass. Fasteners and the full mating harness remain absent.

`assembly-data/JLC_SMT_BOM.csv` and `JLC_SMT_CPL.csv` contain exactly the same
81 fitted SMT parts. The PH header is listed separately for hand soldering. Seven
bare test pads and the three optional encoder DNP parts are excluded. Supplier
rotations are checked against native R0 renders of the genuine imports; the LED's
small original pad skew has a documented orientation-metadata classification.
The CPL uses the board lower-left origin in millimeters. Factory machine-origin,
polarity preview, stock and first-article acceptance remain required.

## Manufacturer drawing issue being corrected

The newly retrieved GCT USB4145 drawing A2 (31 January 2023), sheets 1–2,
specifies two locating pegs and two 0.71 mm PCB locating holes per connector.
The original imported footprint contains only the left hole. Both USB connectors
therefore need their right locating hole added. The current 15 V bottom trace
crosses the data connector's missing-hole location and must be rerouted. The
earlier copper/CAM passes do not establish connector assembly fit. Do not order
this checkpoint before that correction and its renewed checks.

The final order must specify 1 oz finished copper on all four layers, green mask,
ENIG and an approved filled-and-capped process for the 0.30 mm vias. The PH
catalog's maximum applicable PCB thickness is 1.6 mm; actual upper thickness
tolerance needs supplier acceptance. The minimum retained via is 0.45/0.30 mm.
No stock is reserved, no JLC order has been submitted, and motor current, hot
operation, regenerative overshoot, harness termination and mechanical tolerances
have not been physically qualified.

Reproduce the fixed native routing source with:

```sh
python scripts/build_controller_pcb.py --check
bun scripts/check-controller-pcb.tsx --report-only
python scripts/audit_controller_pcb.py
python scripts/audit_core_clock.py --controller
python scripts/review_controller_native_drc.py
bun scripts/export-controller-review-cam.tsx
python scripts/audit_controller_cam.py
```

Use the frozen project toolchain and the documented CAD/CAM Python environments.
`constructed-connections.json` is native fixed routing source. The grid router
is retained as construction history; it is not required to reproduce this layout.
