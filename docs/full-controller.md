# Full controller source candidate

The native tscircuit source is `src/controller/board.tsx`, exercised through
`examples/full-controller.circuit.tsx`. This entry documents the unrouted electrical source. The
[routed native PCB](full-controller-pcb.md) and front-carrier assembly are also
provided; neither is a manufacturing release. The separately published MCU prototype remains
available and retains its original validated scope.

All 92 source components from the exact published NEMA14 v1.13.0 are present.
The immutable reference manifest and `scripts/verify_controller.py` compare all
341 remaining physical terminals, including intentionally unconnected pins.
The reference's two unused SH hold-down terminals are absent from the genuine
PH connector footprint. The optional AS5600 and its two capacitors remain DNP. Seven bare PCB test
pads are explicitly doNotPlace so they cannot become purchased BOM items.
The vertical PH footprint declares insertion from above the board.
No NEMA14 repository files were changed remotely.

The explicit part changes are: the 39 kΩ VREF divider resistor becomes
20 kΩ C4184; both 0.24 Ω shunts become genuine 1/3 W HP05W3F240LT5E
C7434086 with unchanged supplier copper pads; and the motor header becomes JST B4B-PH-K-S(LF)(SN), C131334.
The latter is a through-hole part requiring a separate hand-assembly operation
unless a supplier explicitly quotes that process. Supplier copper land patterns and original OBJ/STEP models are preserved.
The project wrapper adds the manufacturer-required second USB locating hole
to both USB footprints; the original supplier files remain unchanged. Source originals and input hashes are
retained; React imports and model URL transport are the working-source changes.

The PH header needs more area than the reference SH header. The candidate board
extends the power-input edge by 5 mm to 35 × 40 mm, with outline coordinates
X = −17.5…17.5 and Y = −17.5…22.5 mm. J_PD moves 5 mm toward that edge;
J_MOTOR, D_DATA and R_STATUS_B move to avoid native courtyard conflicts. All
other component poses remain inherited. Existing routing cannot be assumed
valid after these changes. PCB holes at 26 mm pitch are an adapter interface;
they do not fit or establish motor mounting threads. The motor only documents
front M2.5 threads at 23 mm pitch. The original front-anchored carrier proposal provides this separate interface.

`npm run controller:build` checks the strict native schema, placement and model
asset availability. `npm run controller:check` verifies pin and value parity.
`npm run controller:3d` exports a native GLB using the actual supplier OBJ models.
This command exports a PCB review artifact. The separate native assembly includes
the OEM motor and proposed carrier; mating housing, crimp contacts, full leads
and fasteners remain absent. Independent STEP sections verify the PH lead row
and both USB connectors' four shell stakes and two locating pegs. PH needs a documented +0.5500383 mm local Y assembly-pose correction;
the supplier files and PH holes remain unchanged. USB models receive a +0.05 mm
global Z pose correction to align the SMT contact datum with the PCB top.
Full assembly tolerances and tool access remain independent release checks.
The independent nominal audit finds no solid collisions among 82 fitted parts.
OCCT flags the original GCT USB STEP compound as invalid for both USB parts;
that supplier input limitation is retained in the audit, not silently healed.

The motor's AWG26 UL1569 leads do not fit the reference SH contact's AWG32–28
range. The manufacturer PH catalog identifies PHR-4 and SPH-002T-P0.5S for
AWG30–24, but requires 0.9–1.5 mm insulation diameter. Measure the actual
OEM lead insulation and obtain strip-length, crimp-height and tooling instructions
before approving termination. Do not trim strands
to fit a contact. OEM pin order is 1 A+ black, 2 A− green, 3 B+ red, 4 B− blue;
verify the mating-face view before termination. No rear holes or shaft are assumed.

The current candidate is 0.572917 A peak, about 0.405113 A per phase in full-step.
The conditional 64-corner screen reaches 0.657640 A, including ±3 µA VREF input
current. The assumed ±5% driver allowance is not a manufacturer guarantee at
VREF = 1.1 V. Both original 125 mW shunts have been replaced with 1/3 W parts: each
dissipates 107.736 mW at 0.67 A, or 32.3% of its 70 °C ambient rating.
The manufacturer curve derates linearly to zero at 155 °C; this is an ambient
curve, not a predicted resistor body temperature. Pulse and post-reflow behavior
remain unqualified. See `design-review.md`
and `artifacts/requirements/current-budget.json` for thermal scope and limits.

The source build has no routed copper. Six functional A4 sheets and independent
visual ERC are provided. The separate routed milestone includes DRC review,
independent connectivity/shorts/CAM checks, native motor/carrier assembly and
exact candidate assembly BOM/CPL. Current measurements, thermal qualification,
stock, harness and JLC process acceptance remain release requirements. The existing MCU-only
Gerbers must never be ordered as a complete motor controller.

Native source diagnostics report zero errors/warnings. The pin-specification
checker reports nine metadata warnings for supplier-imported protection,
transistor, RGB and buzzer symbols: these devices do not all have direct power
or ground pins. These warnings remain visible in `native-pin-specification.txt`;
they are not a full ERC waiver. This CLI version's netlist subcommand does not
accept a Circuit JSON array; its TSX source check is recorded separately.

## Native motor clearance arrangement

`examples/controller-assembly.circuit.tsx` uses a native `assembly.part` with
the OEM motor STEP and an OBJ tessellated from that unchanged STEP. It preserves
the exact electrical, PCB, schematic and component CAD records. The front datum
is Z = −42 mm and the motor rotates +90° about Z so its fixed leads exit positive
X toward the JST side. No generic NEMA motor model is substituted.

`development-assembly.glb` includes the original proposed front carrier. The
full harness and actual fasteners remain absent. The drawing's maximum
33 mm body leaves 8.2 mm to the PCB bottom in this position. The native GLB is
checked against all 82 supplier STEP bounds and the OEM motor/carrier bounds after the
exporter's global coordinate transform. This is not a demonstration of usable
rear mounting holes, an encoder magnet, qualified tolerances or thermal behavior.

## Copper and fabrication development

The working full-board routing is under independent and native checks in
`artifacts/controller-pcb/`; it is not a release. The order must specify **1 oz
(35 µm) finished copper on all four layers**, 1.6 mm thickness, green mask and
ENIG. JLCPCB defaults to 0.5 oz inner copper, which does not meet the selected
0.67 A / 30 °C legacy internal-trace screen for a 0.30 mm path.

The selected via process is IPC-4761 Type VII epoxy fill and copper cap on
0.30 mm vias only. Leave component holes and mounting holes open. JLCPCB
publishes this process for four-layer boards, subject to quote/CAM acceptance.
Its published preferred via pad diameter is drill + 0.15 mm, compatible with
the retained 0.45/0.30 mm geometry. This nominal capability is not vendor
acceptance of this board. See the dated published-capability evidence.
