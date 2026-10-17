# NEMA11 RP2040 controller source prototype

**Unrouted electrical and schematic prototype. Not fabrication ready.**

This native tscircuit package contains the complete controller source milestone:
92 components, 341 physical terminals, six functional A4 schematic sheets and
original supplier component models. It preserves the published NEMA14 v1.13.0
features. Explicit changes are a 20 kΩ VREF resistor and a JST PH motor header.
The optional AS5600 and its two capacitors remain DNP.

Every physical terminal and component value is checked against the exact
reference, with the two part changes and removed SH hold-downs documented.
Independent schematic geometry/ERC checks connected symbol pins and named nets.
Native source checks pass; nine supplier-symbol pin metadata warnings remain.
The original USB STEP file has an OCCT validity limitation. Nominal component
collision and connector lead/hole checks are documented in the GitHub artifacts.

The 35 × 39 mm board has no routed copper in this package. PCB holes at 26 mm
pitch are an adapter interface, not motor attachment holes. The motor drawing
only specifies front M2.5 threads at 23 mm pitch. No rear holes or shaft are
assumed. A motor carrier, mating housing, contacts, wiring, hardware and physical
assembly qualification remain required.

The nominal driver limit is 0.572917 A peak. Tolerance screening is conditional;
current accuracy at this VREF, thermal performance, sense resistor derating,
regeneration, fabrication process requirements and supplier stock are unqualified.
Do not order the MCU-only review Gerbers as a complete controller.

Use `tsci dev index.circuit.json` to open the native design, or
`tsci build index.circuit.json` to reproduce the package build. Full TSX source,
supplier imports, the verified six-page PDF, native GLB and independent check
reports are in [NEMA11_RP2040](https://github.com/AnasSarkiz/NEMA11_RP2040).
`package-verification.json` is the pre-upload source receipt; the GitHub
publication artifact records independent verification after upload.
