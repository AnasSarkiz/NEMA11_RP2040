# NEMA11 electrical, mechanical and tool review

The existing NEMA11 project continues unchanged in identity: 28 × 28 × 1.6 mm,
two copper layers, required buzzer, 0.67 A motor and original four motor-bolt
axes. No new V2, public push, registry publication, routing or order occurred.
This checkpoint preserves useful engineering work and an **unverified current
main placement**, not a release.

## Verification state

The latest main source contains the improved pose described below. Local
formatting, TypeScript and 25 prebuild regressions pass. Its main native run
did not complete; no fresh main circuit JSON or build receipt was emitted.
External-service validation traffic needs approval before that run resumes.
Native-dependent current gates have therefore not passed. The last completed
main verification is commit `7da9556`; its history and evidence are retained.

The new placement was separately native-built in an isolated study before
integration. This evidence is under the board's
`references/electrical-placement-20261109/`. It retains two USB courtyard
boundary errors and no nested native PCB errors. The placement tool's separate
advisory summary still reports three DNP-encoder courtyard collisions and nine
suboptimal orientations, as before. Optional encoder assembly clearance is
not approved. No finding was waived or hidden.

The verification runner now invalidates old summary success before each stage,
preserving a partial failed status if interrupted. A regression exercises this
without invoking native tools or network requests. Current status explicitly
marks the main native-dependent checks incomplete.

## Placement changes and limits

Actual pad-edge lower bounds, not component-center or routed distances:

| Connection | Previous | Candidate |
| --- | ---: | ---: |
| RP2040 pin33 to C_IO33 | 2.9825 mm | 0.5550 mm |
| A4988 VREG pin8 to C_VREG | 2.7765 mm | 0.6000 mm |
| A4988 VDD pin15 to C_DRV_LOGIC | 4.0950 mm | 2.0900 mm |

The other 42 measured pairs are unchanged; both additionally reviewed driver
capacitor ground-return bounds improve. Most MCU/clock/flash/decouplers shift
rigidly by +0.053998 mm Y. The motor header shifts −0.025003 mm X; reviewed
anchor expectations explicitly record that change, while motor-hole axes,
USB anchors and centered encoder remain unchanged.

Conservative nominal head-envelope margin changes 0.044548→0.0749997 mm;
copper-edge margin 0.361098→0.389003 mm; minimum same-layer copper remains
0.160 mm. The tiny head-margin gain is sensitivity evidence, not useful
manufacturing-tolerance qualification. No actual bolt tolerance was assumed.

Major remaining pad-edge lower bounds are buck input supply/ground 4.941 mm,
driver VM supply 6.990/4.158 mm, crystal XIN 4.399 mm, USB DP series resistor
4.159 mm and QSPI clock 14.003 mm. These are layout-review concerns rather
than universal distance limits or proof of electrical failure. Larger trial
repacking was rejected because it created collisions or worsened returns.
Clock, decoupling, switching loops, sense returns and signal corridors remain
unqualified. The RP2040 guide's permitted shared-decoupling trade-off for
adjacent pins48/49 is retained in the review, not replaced by a rigid
one-named-capacitor-per-pin rule.

`electrical-placement/` contains portable calculations, SHA-bound inputs,
integrated comparison, negative trials, source citations and reproduction
instructions. This is unrouted WIP, not electrical acceptance.

## Upright USB and all-top assembly

Fresh supported C5815189 import reproduces EasyEDA's oversized locator slot:
1.509979 × 0.709981 mm versus GCT A2's 1.01 × 0.71 mm ±0.05. Raw supplier
geometry, native output and exported drill agree. The current importer is not
the cause of this discrepancy. No supplier geometry was patched locally.

C5181332 cannot be imported from the supported source; C5291559 imports but
its 1.09982 mm slot also exceeds the drawing's 1.06 mm upper limit. No checked
upright candidate is qualified. Native C5815189 CAM also contains bottom paste
apertures on shell stakes. This needs a supported correction/configuration or
assembler-approved process; it does not prove mixed SMT/THT assembly with all
components on top is impossible.

Current fitted courtyard sum is 765.793 mm². Hypothetically substituting two
upright courtyards gives 679.354 mm², leaving about 35.249 mm² against the
714.602 mm² nominal board area excluding provisional head disks. This excludes
DNP encoder reservation, routing, edge/process, plug and access constraints.
It is not a placement or routing proof. No all-top packing trial with an
unqualified footprint is presented as viable hardware.

See `upright-usb-report.md` and the complete `upright-usb-evidence.tar.gz`.
The two-edge fallback remains intact.

## Underside envelope

The official world-coordinate CAD loader and an independent calculation agree
for all 89 fitted imported models. Nominal projections below the board are
1.83 mm for the bottom inductor, 1.649 mm for ESD protection, and 1.40 mm for
the top-mounted motor header's through-hole tails. A hypothetical 2 mm gap
would leave only 0.17 mm beyond the inductor model, before tolerances, solder,
insulation or motor features. This does not qualify that gap or the model's
physical accuracy. Single-sided placement would not automatically make the
underside flat. `underside-envelope/` preserves the measurements and tests.

## Genuine tool defects and integration result

Two generic checks 0.0.270 fixes recognize typed pin attributes and align the
all-passive ground rule with the existing power rule. Ten regressions pass;
pristine code fails seven. Exactly four false warnings disappear, leaving
26 unchanged warnings. Missing metadata is not invented to clear the rest.

A core 0.0.2304 alias-array sizing fix restores the already-existing
string-label sizing behavior. Five regressions pass; pristine code fails
three. Full isolated board rendering clears both imported-label findings and
preserves every physical PCB, CAD and electrical graph record exactly.
However, 12 larger schematic boxes change automatic trace routing and expose
a new U_BUCK.FB path-spread finding: overall schematic findings are **3→2**,
or **1** when combined with the separate bootstrap analyzer candidate, not
zero. External metadata timeouts also remain visible in that run.

The candidates are not installed in the main board and have not passed full
upstream suites/CI. See `tool-candidates-report.md`,
`tool-candidates-full-board-report.md` and `tool-candidates-evidence.tar.gz`.
The full negative integration result is retained, not normalized away.

## Next steps

1. Resume current main native verification only after external validation
   traffic is approved; retain every diagnostic and freshness check.
2. Repack the unresolved functional clusters and review actual routing/return
   corridors, then rerun source and geometric checks.
3. Obtain a supported corrected upright footprint or qualify another exact
   part, and resolve shell-anchor assembly/paste treatment before an all-top
   trial. Do not infer fit from the area screen.
4. Resolve tool integration's new schematic path issue and supported imported
   pin metadata, without overriding supplier definitions or suppressing checks.
5. Obtain actual rear-fastener, gap and motor/interface evidence before any
   fit claim; then qualify panel, assembly and hardware behavior. Routing and
   fabrication remain gated separately from local software test success.
