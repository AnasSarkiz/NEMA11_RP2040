# NEMA11 RP2040 compact placement prototype 0.1.0

**UNROUTED DEVELOPMENT MILESTONE — DO NOT FABRICATE.**

Native tscircuit full controller source, six connected A4 schematic sheets,
82 genuine supplier component models, the unchanged OEM 11HS12-0674S motor and
a custom front-anchored compact carrier proposal. All fitted electrical parts
are on top of a nominal 28 × 28 mm PCB; their nominal bodies fit within the
motor drawing's 28.3 × 28.3 mm maximum frame. The optional encoder remains DNP.

92 electrical components, 340 physical terminals and all 64 reference functional
nets are preserved. The smaller genuine MLT-5020 buzzer removes one dummy NC
terminal; the PH motor connector, 20k/10k reference divider and rated 0.24 ohm
shunts are documented changes from exact published NEMA14 v1.13.0. NEMA14 is
unchanged.

Native source/pin/netlist/schematic checks pass. Independent checks verify all
340 original supplier pad geometries, zero touching pad pairs, minimum 0.199619
mm foreign-pad gap, 0.255 mm copper-edge clearance and 2,346 nominal JLC
component spacing pairs. Six-sheet drawing/ERC and all 84 native 3D bounds pass.
These are placement/source results, not a zero-open routed PCB certificate.

**Remaining requirements:** complete copper routing, clock/USB escape paths,
USB impedance/stackup, grounding, thermal/current/regen qualification, final
readable silkscreen, exact routed BOM/CPL/CAM, panel/process/stock acceptance,
manufacturer dimensional tolerances, full harness/plug/contact/wire-OD validation
and genuine fasteners. The compact carrier uses the motor's front threads only;
its narrow corner rails need OEM corner-radius acceptance and strength testing.
No rear motor holes or rear shaft are invented. The original GCT STEP compound
validity limitation remains reported; its nominal solids and connector hole fit
pass. OEM lead stubs extend beyond the frame; arbitrary cables are not covered
by the PCB component-body fit result.

[Source and review artifacts](https://github.com/AnasSarkiz/NEMA11_RP2040)
