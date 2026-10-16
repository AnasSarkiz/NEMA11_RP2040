# Native tscircuit MCU PCB development milestone

This is the routed **MCU subsystem**, not the complete NEMA11 controller or a
fabrication release. Open external circuits remain explicit. The source is
native tscircuit TSX; saved routing, planes, supplier CAD and symbol connections
are native Circuit JSON. `tsci build artifacts/rp2040-pcb/board.circuit.json`
reproduces the saved board without changing its records.

- [Native routed PCB](../artifacts/rp2040-pcb/board.circuit.json)
- [Native 3D assembly GLB](../artifacts/rp2040-pcb/development-pcb.glb)
- [Top copper review](../artifacts/rp2040-pcb/top.png)
- [Three functional A4 schematic sheets](../artifacts/rp2040-core/schematic-a4.pdf)
- [Native checks, including outstanding external connections](../artifacts/rp2040-pcb/native-drc.json)
- [Independent copper audit](../artifacts/rp2040-pcb/independent-copper-audit.json)
- [Crystal layout audit](../artifacts/rp2040-pcb/clock-layout-audit.json)
- [Nominal supplier-solid assembly audit](../artifacts/rp2040-pcb/nominal-assembly-audit.json)

## Routing and supplier provenance

The 35 × 35 × 1.6 mm four-layer board remains a development canvas with **no
mounting holes**. Its size is not an approved fit to the 28.3 mm motor. It
contains the 31-component/119-port subsystem described in `rp2040-core.md`;
24 components have purchased supplier models and seven are bare copper pads.

The routing seed is explicitly from inspected GitHub v1.12.0 commit
`596a8b8a5187dfd60924de4b8ac0c93e13d99680`, not the unavailable requested
published v1.13.0. `src/pcb/core-routing-seed.json` records its original board
hash and physical pin mapping. All 119 supplier pad geometries and positions
must match before any route can transfer. Original reference mounting holes,
other components and their models are not transferred.

The generator remaps physical pin and net IDs, removes absent-component supply
stubs and copper groups serving no retained pad, and binds native route metadata
to a pad in the actual physical copper group. It adds two real 3.3 V fanouts
and recomputes masked ground pours on top/inner1/bottom and a 3.3 V pour on
inner2. Planes clear foreign copper by 0.20 mm and remain 0.35 mm inside the
board. Source net labels alone never establish a physical connection.

The independent audit checks copper separately on all four layers. It includes
pad outlines, individual same-layer trace segments, drilled via annuli and
pour holes; only plated vias join layers. Minimum checks are 0.16 mm trace
width, 0.15 mm foreign-net clearance, 0.25 mm copper-to-edge, and 0.30/0.45 mm
via drill/pad. All internally connected subsystem pad nets pass, with no shorts
or clearance violations under these checks. Seven fault tests exercise missing
copper, incorrect layer changes, shorts, clearance, via and edge failures.

Native `@tscircuit/checks` retains **15 open external-interface errors**, matched
to exact physical pins/nets in `config/core-pcb-scope.json`. These are the
unfinished driver/accessory GPIO and connector-side USB lines. Any additional
error or changed open-interface contract fails the subsystem check. The report
explicitly states that full-controller DRC has **not** passed. Its three
crystal pin-attribute warnings are also retained; this is not a complete ERC
qualification.

Clock routes remain top-only with no signal vias: XIN 3.643 mm, XOUT 4.795 mm,
and XTAL_OUT 2.675 mm total copper. The construction reservation on top/inner1
and short ground returns to inner1 pass. Startup, frequency, load parasitics
and crystal drive remain bench requirements.

## 3D and assembly scope

`circuit-json-to-gltf` creates the native GLB from this routed board and the nine
unchanged supplier OBJ types. All model requests resolve to committed assets;
there is no replacement body geometry or remote fallback. A separate OCCT
check places the 24 original supplier STEP solids using native CAD origin,
rotation and position. It finds no nominal component collisions; the minimum
nearby component surface gap is approximately 0.599 mm.

These are nominal models, not maximum manufacturer tolerance envelopes. The
motor STEP, JST mating housing/crimps, wire colors/pin order, fasteners and
assembly/rework/tool access are not included or verified. No rear motor holes,
rear shaft or speculative adapter appears in this PCB or 3D assembly.

## Manufacturing gates still open

The copper candidate does not qualify the full controller. The reference
silkscreen text is crowded and needs layout/clearance review. Via-in-pad is
allowed only at the inherited MCU grounded exposed-pad site; the other vias
are checked strictly. The fabricator must confirm the required filled/capped
thermal via process and compatible stencil/paste design, or this site must be
redesigned. A 0.45 mm pad around a 0.30 mm hole has only 0.075 mm nominal radial
annulus; finished-hole/tooling tolerances and JLCPCB capability are unresolved.

The final outline, 23 mm front mounting pitch/M2.5 attachment, genuine motor
geometry, CH224A, exact v1.13.0 parity, both USB-C circuits, regulators,
protection, driver/current senses/microsteps, accessory/encoder DNP circuits,
full-board thermal/trace review and motor harness remain outstanding. Supplier
stock has not been refreshed. Do not order this development canvas as the
requested motor-controller board. Production BOM/CPL and release Gerbers are
not supplied for this incomplete circuit.

## Reproduce

Use the frozen tooling from `bash scripts/setup-tools.sh` and put
`tools/pcb/node_modules/.bin` on PATH. `npm run pcb:route` rebuilds the saved
copper; `npm run pcb:check` runs native and independent audits. `npm run pcb:3d`
exports the native 3D assembly. `npm run pcb:dev` opens this exact saved Circuit
JSON in tscircuit. Source, pad/model inputs and routing are retained in GitHub;
this is not a KiCad replacement workflow.
