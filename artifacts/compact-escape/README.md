# Compact clock and USB escape milestone

**PARTIALLY ROUTED DEVELOPMENT BOARD — DO NOT FABRICATE.**

This native tscircuit candidate retains all 92 electrical components and 340
physical pins. All 82 fitted parts are on top. Their nominal supplier STEP
envelopes fit inside 28.3 × 28.3 mm; PCB copper clears its 28 × 28 mm outline by
at least 0.255 mm. Original supplier pads and 2,346 nominal JLC component-spacing
pairs pass independent checks. Actual body tolerances remain unqualified.

The three crystal nets and two short MCU-to-USB-resistor nets are physically
connected on top with no signal vias. Four crystal ground stitches connect to
the MCU exposed-pad ground through inner1. Vias retain 0.30 mm drills and at
least 0.50 mm pads. Independent copper checks find **58 disconnected controller
nets and no shorts, clearance, drill or edge defects**. Full-board DRC is not
passed. These USB escapes do not establish a complete differential data path
or 90 Ω impedance. Long interconnect routing is continuing separately.
The native checker also reports 270 port-connectivity findings; its
complete failing report is retained in `native-drc.json` without filtering.

Six connected A4 schematic sheets pass independent ERC and native source,
pin-specification, netlist and schematic-placement checks. The native GLB has
84 independently checked models: 82 supplier parts, the unchanged OEM motor
and the compact front-carrier proposal. The two original GCT STEP compounds
remain OCCT-invalid; their nominal solids and lead/locating-peg fit pass. No
rear motor holes or rear shaft are invented. The optional encoder remains DNP
at the motor axis; no operating encoder/magnet attachment is claimed.

`placement-source.json` reproduces `unrouted.circuit.json` using:

```sh
bun scripts/build-controller.tsx --compact \
  --placement artifacts/compact-escape/placement-source.json \
  --out /workspace/.cache/nema11-reproduced-escape
```

Power and decoupling placement budgets use explicitly recorded connection
points inside unchanged native copper for four links. Independent checks
confirm the points are at least 0.049 mm inside the pads. The original 2.8,
3.5 and 4.0 mm connection budgets remain unchanged; real routed decoupling
and power-loop review is still required.

Motor connector placement is lower than in prototype 0.1.0 to provide room for
the catalog's 8 mm mated JST PH height alongside vertical USB cables. Genuine
PHR-4/contact CAD, actual USB overmold dimensions, wire outside diameter,
termination, bend/strain relief and fastener qualification remain unresolved.
The narrow custom carrier rails require strength and vibration validation.
Current accuracy, thermal/regen behavior, buzzer drive/reflow, stackup,
assembly process, panel and live stock remain unqualified. No compact final
BOM/CPL/Gerber release is represented by this milestone.
