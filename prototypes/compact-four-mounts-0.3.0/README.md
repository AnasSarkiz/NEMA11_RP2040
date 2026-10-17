# Four-corner NEMA11 compact development candidate

Native tscircuit 28 × 28 mm PCB, with **four Ø1.8 mm NPTH mounting holes on a
25 mm square**. Each hole has a Ø3.2 mm four-layer head/copper exclusion; the
nominal head envelope fits within the motor's maximum 28.3 × 28.3 mm frame.
The hole edge has 0.60 mm nominal laminate to the PCB edge.

NEMA14 v1.13.0 used four Ø3.2 mm holes at 26 mm pitch and Ø6.4 mm head exclusions.
Those dimensions cannot fit this outline. The four-corner arrangement is
retained with smaller candidate M1.6 PCB fasteners. Genuine fastener maximum
head/tool dimensions, engagement, torque and carrier qualification remain open.
These PCB holes attach to a separate carrier, not to invented motor rear holes.
The motor has four verified **M2.5 front threads at 23 ±0.15 mm pitch**, minimum
thread depth 3.5 mm.

The user authorized removing the buzzer if necessary for four mounts. This
candidate removes BZ1, Q_BUZZER, D_BUZZER, R_BUZZER_GATE, R_BUZZER_PD and C_BUZZER;
GPIO16 is explicitly NC. The complete remaining reference feature set is checked
against the immutable published reference: 86 components, 326 physical pins,
76 fitted electrical parts on top, seven bare test pads and three encoder DNP
footprints. Six connected A4 schematic pages are exported to `schematic-a4.pdf`.

Source, supplier-pad geometry, nominal assembly envelopes, four-head clearance,
component spacing, pin parity and schematic/ERC checks pass. Original GCT USB
STEP compound validity errors remain explicitly reported; nominal solid/lead
fit checks pass. Manufacturer dimensional tolerances are not qualified.

The native `assembly.circuit.json` and `development-assembly.glb` include 78
checked models: 76 supplier parts, the genuine OEM motor and the four-piece
carrier proposal. Exported bounds match original CAD within 0.05 mm.

The custom four-piece front carrier proposal is a mechanical review artifact.
It has four PCB support locations and four separate radial assembly paths;
48 sampled positions have no nominal motor/quarter collisions. Extremely narrow
corner rails, OEM corner tolerances, stiffness, vibration, actual fasteners and
continuous insertion/tool access require further work. It is not an approved
carrier or an assembly-ready design.

**Routing is incomplete. No zero-open, zero-DRC or fabrication-ready claim is
made. Do not order from these development files.** Earlier two-hole compact
prototype versions remain immutable historical candidates and do not meet the
new four-hole requirement. The routed 35 × 40 mm baseline is also historical.
