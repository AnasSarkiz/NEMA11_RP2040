# Motor-face compact redesign

The active [four-hole candidate](four-mount-compact.md) supersedes the two-hole
placement milestones described below. It has 76 fitted parts on top, with the
complete buzzer circuit removed under the user's explicit authorization. All
other features remain checked. The 0.1.0 and 0.2.0 prototypes below are frozen
historical checkpoints; latest 0.3.0 is the unrouted four-hole source/3D snapshot.

The user requires the PCB and installed USB/JST/component bodies to fit within
the motor's **28.3 × 28.3 mm maximum frame**. The OEM drawing A0071 revision 2
states that maximum; it does not state a 28.0 mm nominal frame. The initial PCB
target is 28.0 × 28.0 mm, subject to finished-outline tolerance acceptance.
The preceding routed 35 × 40 mm controller does **not** meet this new envelope.
Its zero-error DRC/connectivity results remain a useful electrical baseline.

All 82 fitted baseline components are on top. Seven bare test points are also
on top; the three optional encoder footprints remain DNP. All-top placement and
an SMT-only manufacturing process are distinct requirements: the existing PH
header and USB shell stakes need through-hole soldering. The user confirmed that all fitted parts must be on top; through-hole
soldering is allowed. The compact candidate therefore retains the genuine
through-hole PH header and upright USB connectors.

The conservative top-side envelopes combine genuine copper, authored courtyards
and original supplier STEP bounds. For 89 top-side components/test points they
total 808.796 mm², larger than both a 28 × 28 mm PCB (784 mm²) and the maximum
frame square (800.89 mm²), before mounting/routing space. This is a rectangular
courtyard packing constraint, not a proof that every possible physical layout is
impossible. It establishes that a simple scaling or translation of the old board
is inadequate. Supplier footprints/models must not be scaled.

Two genuine native JLC imports are retained as candidates, not approved blanket
substitutions:

- C94598, HUAWHA/Huaneng MLT-5020 magnetic buzzer. The manufacturer specification
  dated 2021-05-27 gives 3 V rated, 2–4 V operation, 4 kHz ±200 Hz at 50% duty,
  maximum 100 mA at the rated test condition, 12 ±3 Ω coil resistance and minimum
  75 dB at 0.1 m. It has three solder terminals, including one dummy NC. The
  dimensional table says 5.2 ×5.2 ×2 mm; its drawing says 5.0 ±0.3 mm square and
  2.0 ±0.2 mm height. The conservative layout must cover this discrepancy and
  actual model bounds. It preserves an audible indicator but does not promise
  the original buzzer's sound level. Drive/current/thermal and reflow profile
  require review before selecting it. Its 6.8 ×5.76 mm authored courtyard could
  save approximately 63 mm² versus the existing buzzer.
- C160354, JST B4B-PH-SM4-TB(LF)(SN), a genuine top-entry SMT PH header with six
  pads including two hold-downs. It uses more area than the through-hole version;
  manufacturer land pattern, crimp/housing compatibility and supplier process
  acceptance still require validation. Its import alone does not solve fit.

The 3.3 V nominal rail lies inside the MLT-5020 operating range, including the
existing ±5% screen. The existing AO3400A switch and B5819W flyback path remain
part of the candidate circuit. Worst-case DC coil current at 3.465 V and 9 Ω is
385 mA; that is not its rated 4 kHz operating-current guarantee. Recalculate the
logic budget and require the documented waveform instead of assuming a DC tone.

General JLC text search currently returns unrelated matches, even for exact
known part names. Candidate identity comes from structured connector records,
exact LCSC product pages, original manufacturer documents and actual native
imports. Search-result stock must not be treated as qualified availability.
No stock is reserved.

`config/compact-controller-requirements.json` records the target.
`artifacts/requirements/compact-supplier-candidates.json` hashes the untouched
imports. Native compact source, supplier-model envelope checks, mechanical
attachment, routing and manufacturing checks must pass before replacing the
validated electrical baseline or claiming compact fabrication readiness.

The current construction search also checks JLCPCB's [minimum component spacing
recommendations](https://jlcpcb.com/help/article/minimum-spacing-for-smd-components),
updated 2026-09-09. Its measurement diagram includes protruding component leads;
this is not merely a plastic-body or copper-pad spacing rule. QFN-to-chip spacing
is 1.0 mm, for example. `compact-JLC-component-spacing.json` records the table and
source hashes. A second search envelope uses the union of original copper and
nominal supplier STEP bounds plus 0.10 mm per side, with the larger package-pair
spacing rules enforced separately. This is construction geometry, not a silently
approved supplier courtyard, tolerance qualification or a fabrication release.
The unchanged original imports and their courtyards remain preserved.

The full controller source now accepts an optional mechanical/placement profile.
The existing default builds to the identical source circuit SHA256
`4a84dcb42e7f4ee19bf6bdd294a5291d00bd7963d07783f2328cbc1cfe5b8144`.
No compact routing or compact assembly validation is claimed by that refactor.

## Validated placement milestone

The native 28 × 28 mm development source contains 92 electrical components,
340 physical terminals and all 64 functional nets. The selected MLT-5020 removes
one unused dummy buzzer terminal; all 304 connected terminal assignments match
the exact reference after the documented current-limit/PH/shunt changes.
All 82 fitted parts are on top; the optional encoder and its capacitors remain
DNP, and the seven bare test pads remain accessible on top.

For source SHA256 `78a201d31baaf11b8896d285a3e697710d2eae2a403ab7bf5303028735e1ed62`:

- Native rendering has no source/schema/placement errors.
- All 340 supplier pad geometries are unchanged after rigid placement transforms.
- Independent pad checks find no shorted pad pairs, minimum foreign-pad gap
  0.199619 mm and minimum copper-to-edge distance 0.255 mm.
- All 2,346 applicable component-pair spacing checks pass at nominal model size.
  The smallest surplus over the JLC recommendation is 0.005 mm; this is **not**
  a tolerance-qualified manufacturing margin.
- All 82 original supplier solids fit the 28.3 mm frame; nominal assembled body
  bounds are X −13.9571…13.8928 mm, Y −14.0400…14.0400 mm. No solid collisions
  or connector lead/hole misalignment were found. The original GCT STEP compound
  validity limitation remains reported, without healing or replacing its model.
- Six A4 schematic sheets cover every physical terminal with connected symbol
  pins or explicit NC marks. An independent drawing/ERC check passes.
- The native controller GLB loads 45 distinct genuine model assets.

This is an **unrouted placement milestone**. The routing construction file is a
separate intermediate with opens and unqualified USB pair geometry, never a
manufacturing board. The first routing pass exposed blocked MCU escape paths;
placement/routing refinement is in progress. Supplier silk also needs final
legibility and mask/edge processing after copper is settled.

The custom compact carrier proposal fits within the frame at nominal geometry
and has no volume intersection with the original OEM STEP. It uses front M2.5
threads and two PCB M1.6 supports, with no invented rear motor holes. The motor
STEP has R3 rounded corners, not straight chamfers. Corner dimensions are absent
from the drawing; the very narrow carrier rails require OEM dimensional
acceptance plus strength, vibration and thermal validation. It is a custom
proposal, explicitly not genuine supplier hardware or a released manufactured
part. The original motor STEP includes wire lead-outs beyond the frame; the PCB
body fit above does not claim that unbent motor wires or arbitrary cable plugs
fit within that square. Full harness routing remains to be qualified.

The complete native compact assembly GLB independently matches all 84 supplier,
OEM motor and custom-carrier STEP bounds. It retains the original motor lead
stubs toward +X and the top-entry PH edge. Full harness and genuine fasteners
are still absent. The separate native package
[`AnasSarkiz/NEMA11_RP2040_Compact_Prototype`](https://tscircuit.com/AnasSarkiz/NEMA11_RP2040_Compact_Prototype)
version 0.1.0 freezes this **unrouted** placement/source/assembly milestone.
The actual configured CLI authentication, native build roundtrip and compressed
CLI push succeeded; the public registry files are independently checked against
the local snapshot. No credential is included in that snapshot or the repository.

## Clock routing construction

A separate development placement moves the bypass capacitors that obstructed
XOUT and reserves a 0.55 mm crystal escape corridor. Its source hash is
`dd13c56231445941389045e1f64c7eaf8d5b409c491fa1eda1ccbfef5e9998a4`.
All 340 supplier copper shapes, all 304 reference connected-pin assignments,
all-top placement and the frame/pair-spacing construction checks still pass.
The minimum nominal JLC spacing surplus improves to 0.040 mm.

`artifacts/compact-clock` freezes only the clock and local ground construction.
XIN/XOUT/XTAL_OUT have one physical copper island each, top traces only, no
signal vias, and total wire lengths 2.880/1.480/0.747 mm. Four actual clock/load
returns are within 1.2 mm and physically join the RP2040 exposed pad through the
inner1 ground plane. The original 0.25 mm top/inner1 guard and 0.55 mm MCU-pin
local exemption pass. Three exposed-pad barrels require filled/capped Type VII
processing. Independent copper/drill/edge/keepout checks find only the expected
61 disconnected nonclock nets in this limited construction; no shorts or
clearance violations are hidden or waived. It is not a completed controller PCB.

MCU through-via fanout and full routing continue separately in
`artifacts/compact-routing`. A rotated optional DNP encoder footprint is being
evaluated at the motor axis to free via space. Neither its DNP status nor its
circuitry is dropped. Genuine PHR-4 and PHR-4-BK housings are catalogued, but native
CLI imports of C111514 and C493120 found no EasyEDA model/footprint. No substitute
housing CAD has been invented; mating/harness qualification remains open.
