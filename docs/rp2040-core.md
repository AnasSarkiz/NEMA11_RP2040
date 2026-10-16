# RP2040 subsystem milestone

`src/rp2040-core.tsx` is the controller's reusable MCU subsystem. Its separate
`examples/rp2040-core.circuit.tsx` canvas is **not the final NEMA11 board**: it
retains the inspected reference's 35 mm development area and component poses,
has no mounting holes and is intentionally unrouted. No Gerbers or order BOM/CPL
are exported from this canvas.

## Implemented circuit

The 31 components provide RP2040, GD25Q16EEIGR 2 MB QSPI flash, 12 MHz
ABM8-272-T3 crystal, six IOVDD bypasses, two DVDD bypasses, USB/ADC bypasses,
VREG input/output capacitors, flash bypass/pull-up, oscillator load capacitors
and 1 kΩ damping, two 27 Ω USB resistors, RUN pull-up and seven bare debug pads.

All six IOVDD pins, ADC_AVDD, USB_VDD and VREG_IN connect to 3.3 V. VREG_OUT
and both DVDD pins connect to the separate nominal 1.1 V rail. TESTEN and the
exposed ground pad connect to GND. All flash IO pins connect to their numbered
RP2040 QSPI signals; no IO2/IO3 substitute pull-up hides a missing connection.

The surrounding controller must supply regulated 3.3 V and connect the named
GPIO interfaces, USB connector/ESD, PD, motor driver, accessories and ADC
dividers. Those external interfaces are **not complete circuits in this
subsystem**. Existing v1.12.0 GPIO allocation is provisional until exact
v1.13.0 source comparison; CH224K is not included as a CH224A substitute.

BOOT entry uses TP_BOOT to TP_BOOT_GND through the 1 kΩ flash-CS resistor while
resetting RUN. SWCLK, SWDIO, RUN, 3.3 V reference and GND remain accessible.
Seven pads have no purchased part and no stencil paste. ROM USB enumeration,
flash boot-stage compatibility and actual flashing remain bench checks.

## Genuine cached supplier data

The nine supplier types were copied from the existing exact JLCPCB imports at
NEMA14 GitHub commit `596a8b8a5187dfd60924de4b8ac0c93e13d99680`. This is a
reuse of cached supplier data, **not a successful new JLCPCB import**. Original
import TSX, OBJ, STEP and cached manufacturer PDFs are committed. Their hashes
are recorded in `artifacts/rp2040-core/supplier-provenance.json`. No supplier
land dimensions, courtyards or model transforms are replaced. Generated native
CAD URLs are pinned to that immutable reference commit.

Manufacturer evidence read for this milestone:

- RP2040 datasheet §1.4: USB termination, 12 MHz boot clock and reset/debug;
  §2.9: all supply rails and bypass requirements; §2.10: regulator output.
- GigaDevice GD25Q16E Rev 1.2, December 2021, page 5: physical flash pin map
  and CS#/WP#/HOLD# behavior. Device-specific boot-stage behavior needs testing.
- Abracon drawing 456603 Rev IR, November 2023: 12 MHz, 10 pF load, 50 Ω ESR,
  10 µW typical / 200 µW maximum drive. Two 15 pF capacitors imply approximately
  2.5 pF assumed stray load; actual parasitics/startup/drive need validation.

## Reproduce and assess

After `bash scripts/setup-tools.sh`, add `tools/pcb/node_modules/.bin` to PATH.
Run `npm run typecheck`, `npm run core:build`, `npm run core:check`, and
`npm test`. Build receipts and native source/CAD are in `artifacts/rp2040-core/`.
The physical-pin checks cover all 119 source ports and exact support values.
Fault-injection tests reject a 3.3 V core-rail error, swapped flash IO2/IO3,
missing bypass, BOOT-to-ground short and paste on a debug pad.

`npm run core:schematic` creates the three functional native schematic sheets
and [A4 vector PDF](../artifacts/rp2040-core/schematic-a4.pdf). The generator
preserves every electrical/PCB/CAD record, uses real supplier-symbol ports,
and connects each used pin to its actual source net. Unused GPIO have NC
crosses. The sheet groups cover MCU/controller interfaces, flash/clock/debug/
USB termination, and the decoupling banks. Native schematic placement reports
zero issues. Geometry checks cover all 119 pins, including wire-to-pin contact
and correct label attachment. Four additional fault tests detect missing pins,
gapped wires and wrong labels. All 14 current tests pass.

`npm run core:3d` produces [development-core.glb](../artifacts/rp2040-core/development-core.glb)
through the native Circuit JSON-to-GLTF converter. It loads the nine original
supplier OBJ types from committed local assets, retains their native poses and
model transforms, and records model hashes. This is an unrouted subsystem
canvas, not the motor/fastener/harness assembly. No motor geometry is invented.

The GitHub workflow rebuilds the subsystem and native schematic, checks pin
connections and source-input hashes, and rejects changed committed JSON output.
Its scope is source/subsystem checks. Workflow publication or execution does
not certify a completed controller or fabrication release.

`/workspace/.venvs/nema11-cad/bin/python scripts/inspect_core_models.py` checks
the nine unchanged STEP inputs for valid solid geometry and records their raw
bounds. Supplier models are nominal geometry, not manufacturer maximum-tolerance
envelopes. For example, the crystal STEP is approximately 3.2 × 2.5 × 0.701 mm;
the drawing describes a nominal 0.8 mm package height. Use drawing limits and
assembly tolerances for final clearance checks, not only these model surfaces.

The development canvas retains minimum 0.30 mm via drills, 0.45 mm via pads,
0.15 mm trace-to-pad/pad-to-pad clearance and 0.25 mm board-edge clearance.
There are no routed traces or vias to qualify in this subsystem canvas.

This is source/subsystem verification. Full-controller ERC, routing, DRC,
crystal/ground layout, thermal review, connectivity/shorts, CAM and completed
motor assembly remain separate outstanding gates. No hardware or fabrication
readiness is claimed.
