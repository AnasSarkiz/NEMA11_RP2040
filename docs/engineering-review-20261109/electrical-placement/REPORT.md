# NEMA11 electrical placement review, 2026-11-09

## Disposition
Do not enable routing or accept electrical fit yet. Native geometric clearance is not evidence of adequate switching loops, decoupling, current-sense returns, or signal integrity. A useful isolated C_IO33 correction was found and evaluated in the native validation study. The other high-priority corrections need coordinated cluster repacking, not unconstrained center-distance optimization. No board/source/import/native JSON was edited by this study.

Baseline: repository HEAD 7da9556d18d4e8b54cc790c58dd25d4b487f34eb; `boards/nema11-rp2040-two-layer--20261022-a1/dist/index/circuit.json`, SHA256 b93b921adc556e840dee2bc4acb0d4f2de8fe990ebf6b6a2638e4636379acf51. Board remains 28×28×1.6 mm, two layers, 99 source/89 fitted components. Genuine emitted geometry and physical pin numbers were used, not symbol orientation or component centers.

## Measurement method
`python review.py` regenerates `metrics.json` with 45 specific pad-pair distances and all pad bounds. It imports the repository's existing conservative geometry-bounds code. Distances are planar Euclidean separation between native copper AABBs, hence lower bounds on trace length, not predicted routing lengths. Rounded pad corners, obstacles, copper width, vias, layer changes and return paths can only worsen/qualify these values. Shared net names are NOT evidence that the same capacitor adequately serves several pins. `nearest_rail_caps.json` checks this ambiguity: C_ADC is the nearest 100nF to MCU43,48,49, but this is not evidence of an adequate shared return topology. The official hardware guide permits a deliberate shared capacitor for adjacent pins48/49 as a two-layer trade-off; it does not establish this scattered placement as adequate. All same-layer metrics are explicitly tagged; USB connector-to-ESD samples require a layer transition.

## Priorities and physical pin topology

### 1. Buck input switching loop and feedback
AP63203 VIN3 and GND4 pads are at (7.6044,12.8362) and (7.6044,10.4364), bottom. Each is at least **4.9409 mm** from the appropriate C_BUCK_IN pad. C_BOOTSTRAP→BST6 is 2.1430 mm and →SW5 is 3.3725 mm. SW5→L_BUCK1 is 1.4481 mm. FB1→C_BUCK_OUT1 positive is 7.6610 mm.

Repack U_BUCK/C_BUCK_IN/C_BOOTSTRAP/L_BUCK/C_BUCK_OUT1/2 as a functional group. For the current U_BUCK pose, CIN belongs on the east side bridging its VIN/GND pad row, positive north and ground south. That space conflicts with the NE bolt envelope, so a small independent CIN move is insufficient. Translate/rotate the buck group inward, keeping its ceramic input loop short and wide, bootstrap loop adjacent, and output feedback taken from the quiet output capacitor side rather than the switching node. Reserve top-side ground under this bottom-mounted converter, with local ground vias. Do not extend SW just to clear a screw. Independent ±4 mm single-part search found no candidate CIN pose under the stated conservative geometry constraints; this is not a proof that the full board is infeasible.

Evidence: Diodes AP63200/1/3/5 DS41326 Rev3-2, p15, recommends nearby VIN capacitors, nearby feedback, substantial ground and ground vias; https://www.diodes.com/datasheet/download/AP63200-AP63201-AP63203-AP63205.pdf .

### 2. Driver supply and current-sense returns
A4988 VBB1 pin22=(3.501,-0.700), VBB2 pin28=(0.499,-0.700), top. C_VM is instead west of the driver: positive-pad bounds are **6.9901 / 4.1577 mm** from pins22/28. Its negative pad is 2.9584 mm from exposed pad29. Repack VM ceramic and sense-resistor cluster along the NORTH edge, with ceramic supply copper feeding both VBB pads and a short broad return toward exposed-pad ground. Existing C_BULK southwest is not a substitute for local ceramic decoupling. If one ceramic cannot serve both pins with a compact loop, evaluate a second genuine imported capacitor through normal source design, rather than modifying footprints.

R_SA→SENSE1 is 1.0474 mm, R_SB→SENSE2 is 2.4296 mm; their ground pads are 2.1251 /1.8844 mm from exposed-pad copper. Retain separate short sense traces and broad local ground returns to the driver ground region, avoiding motor/buck return current through the reference ground. Ground pins3 and18 must join exposed-pad ground. Actual copper widths, thermal vias and current paths remain unimplemented.

CP1/CP2 are on WEST edge at (-0.500,-3.200/-3.700); C_CP pad distances are 2.3255/2.0015 mm. Repack C_CP and C_VCP immediately west of these pads, respecting C_BULK and C_VM relocation. VREG8=(0.499,-5.700) is southwest, whereas C_VREG currently lies southeast: ≥2.7765 mm. Move it below pin8 with local ground. VDD15=(4.500,-4.701) is east, whereas C_DRV_LOGIC is southwest: ≥4.0950 mm. Prioritize moving this capacitor east, adjacent to VDD15/GND18, not toward the visually nearest logic-input pins9–12.

Evidence: Allegro A4988 Rev8 p12 specifies local star-ground/thermal-pad region, ceramic closer to supplies than bulk, and short sense connections with low-impedance ground returns. https://www.allegromicro.com/-/media/files/datasheets/a4988-datasheet.pdf . These requirements do not establish thermal suitability for the specified 0.67 A motor on this two-layer board; characterize it separately.

### 3. MCU physical-pin decoupling
Supply-pin→named-cap positive-pad bounds, mm: IOVDD1 0.5794, IOVDD10 0.5396, IOVDD22 0.5319, IOVDD33 **2.9825**, IOVDD42 1.1176, IOVDD49 **2.1431**, DVDD23 **1.8470**, DVDD50 0.6200, USB_VDD48 **3.6109**, ADC43 0.6277, VREG_IN44 0.9385, VREG_OUT45 **2.4022**.

Concrete independent candidate: **C_IO33 bottom (-12.4915,-6.7459), rotation90**, targeting actual pin33=(-11.2415,-5.9959), reduces bound to **0.5550 mm**. `candidates.py` checks candidate copper ≥0.15 mm from other-component copper (including DNP/through-hole), courtyard ≥0.05 mm, geometry ≥0.15 mm inside board, and ≥0.15 mm beyond each R2.35 bolt envelope. This is a conservative *independent candidate*, not an assembly qualification. The native validation study incorporated it with a small rigid MCU-group translation; see INTEGRATED-REVIEW.md for the exact emitted-pad comparison.

Preserve the good pin1/10/22/50 arrangements. Repack north MCU row capacitors and USB series resistors in physical-pin order: 43 ADC,44 VREG_IN,45 VREG_OUT,46 DM,47 DP,48 USB supply,49 IO,50 core. Place each supply-facing pad toward its corresponding pin and ground-facing pad toward a nearby ground via. A deliberate pin48/49 shared capacitor is an official two-layer design option, but do not infer adequate decoupling merely because C_ADC is nearby on the same rail. Reposition DVDD23 while repacking crystal; it must remain on the V1V1 network.

Evidence: retained manufacturer RP2040.pdf §§2.9.1–2.9.5 and regulator guidance; https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf .

### 4. Crystal and flash
MCU XIN20=(-7.2167,-8.4211), XOUT21=(-7.6164,-8.4211), bottom. XIN→Y_MCU1 is **4.3989 mm**. XOUT→R_XOUT1=2.0681; R_XOUT2→Y3=0.9301; Y1→C_XIN1=1.0459; Y3→C_XOUT1=1.7088 mm. Preserve topology XOUT→series resistor→crystal output/load-cap junction; XIN attaches directly to crystal input/load-cap junction. Reserve a compact bottom-side region just south of pins20/21 for the entire oscillator network, swapping space with C_IO22/C_DV23 if required, and keep switching/motor traces away. Provide quiet local ground for crystal grounds and load capacitors. A greedy six-component group trial did NOT find positions for both decouplers and worsened XOUT path, so **reject `crystal_cluster_candidates.json` as a placement solution**. Keep it only as reproducible negative search evidence.

QSPI CLK MCU52→flash6 is ≥14.0033 mm. Reserve space north of MCU QSPI pins for U_FLASH plus bypass/CS/boot parts, likely requiring relocating low-priority buzzer transistor/indicator passives. Long flash placement is a signal-integrity concern, not an automatic electrical failure; inspect clock/data return continuity and timing after placement.

Manufacturer hardware guide: https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf §§2.3,2.7. Crystal load/drive suitability and startup should be verified with the exact ABM8 part; no claim is made from geometry alone.

### 5. USB/ESD
J_DATA is top, U_ESD bottom. Representative connector8→ESD1 and connector7→ESD3 planar lower bounds are 3.3648 and1.4581 mm, respectively; these are named-pad examples, NOT optimized measurements across all duplicate USB pads. Reserve connector→ESD→series resistors→MCU flow with short connections, a very local ESD ground return and minimal unprotected stubs. Existing ESD5→C_ESD positive and ESD2→negative are both 2.0680 mm. Moving C_ESD closer to one pin alone can worsen the other; prioritize complete clamp/return loop. Pin1/6 share DP and3/4 share DM through the protector. Native net equivalence does not prove routing passes through the protection location.

R_DM MCU46 gap is0.5723 mm, R_DP MCU47 gap **4.1588 mm**. Repack R_DP alongside R_DM at the MCU rather than accepting asymmetric source termination. A continuous return reference is still needed along the full connector-to-MCU route.

Evidence: ST USBLC6-2 DS4260 Rev7 §2.3 p6 calls for short I/O, VBUS and ground connections and protection close to the disturbance source. https://www.st.com/resource/en/datasheet/usblc6-2.pdf .

## Search limitations and next acceptance gates
`independent_candidates.json` is NOT a combined layout: candidates can collide with each other, and some are electrically worse. Only C_IO33 is recommended for immediate native evaluation. Other numerical candidates show where a fixed-neighbor search stalls; they are not approved changes. The greedy crystal result is rejected. No impossibility claim follows from finite grid searches.

After each actual source placement change, rebuild native JSON, rerun nested errors and full geometry checks including original USB courtyard flags, inspect rendered pads, repeat these physical-pin metrics, and manually establish feasible signal/current/ground corridors. Route only after electrical topology review, then verify routed connectivity/DRC, current/thermal performance, power integrity, crystal startup, flash/USB operation, ESD and exact motor mechanical qualification. The existing schematic/pin warnings remain unresolved and cannot be waived by this study.

## Follow-on coordinated placement study
An eight-part top driver repack improved VM and charge-pump supply distances but worsened sense-ground return and REF distances. **Reject `driver_cluster_candidates.json` as an integrated solution.**

A smaller, combined **two-capacitor** change is recommended for native build/inspection, keeping every other original component fixed:
- C_VREG: top (0.7487,-7.2000), rotation0.
- C_DRV_LOGIC: top (4.2500,-7.2010), rotation0.

Results: VREG→driver8 2.7765→0.6000 mm; VREG ground→EP29 2.3733→1.9501 mm. Logic→VDD15 4.0950→2.0900 mm; logic ground→GND18 4.6104→3.5911 mm. This improves both supply and ground bounds without moving the sense or REF components. The same conservative copper/courtyard/board/head tests pass for both simultaneously in the baseline geometry. Reproduce using `python driver_two_caps.py`; poses are in `driver_two_caps_candidates.json`. These exact poses were incorporated in the reviewed native candidate. The remaining long logic ground path is still unresolved, and VM/hot-loop weaknesses are not solved by this change.
