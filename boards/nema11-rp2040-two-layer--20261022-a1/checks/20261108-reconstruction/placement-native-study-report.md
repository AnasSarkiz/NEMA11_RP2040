# New placement study, not native acceptance

Work is isolated in this directory. No main source, imports, footprint, pin maps, symbols, CAD or board settings were changed. No publication or commits. Use only placement-stable.json if integrating, never this copy of the schematic source.

Stable deliverable: placement-stable.json. All 99 placement entries and their sides/rotations are preserved. Frozen USB, motor, bulk, driver, ESD pair anchors and centered DNP encoder are unchanged. All four original bolt axes/holes/head envelopes remain in source. Buzzer moves to left edge region; MCU and clock move left/lower with local bypass constraints. USB remains edge-facing on two adjacent sides. This does not establish all-top feasibility.

Local model derives unmodified courtyard/pad/through-hole dimensions from the fresh 99-part baseline.circuit.json and translates them to each candidate position. Polygon pads use conservative bounding boxes. It checks both sides, through-hole-to-bottom interference, DNP encoder copper, 0.16 mm pad spacing target (above required 0.15), 0.26 mm copper edge target (above required 0.25), and R2.40 bolt-head envelope target (above provisional R2.35). Functional component pairs have soft local-distance constraints. It is not a routing or native acceptance test. Pads of the same component are not pair-checked by this model. Courtyard rectangle overlap can overreport actual polygon/body interference. Native exact geometry remains required.

Measured conservative conflicting component pairs (overlap >0.01 mm in this model) improve from 92 baseline to 32 stable candidate. Components intersecting the provisional R2.35 bolt envelopes improve from 12 to 3. Remaining interference means this candidate is NOT a passing placement; local fit is not established. See local-geometry-measurements.json for exact pairs and overlap estimates. Visuals baseline-local-geometry.png and candidate-local-geometry.png are explicitly labeled translated-baseline geometry, not fresh native PCB renders.

Fresh native build command was attempted with installed tsci versions and routing disabled; build stopped under an API disclosure denial during status polling. The log native-build.log ends at Generating circuit JSON, and no fresh dist/index/circuit.json exists. No retry or workaround was attempted. Therefore baseline native 143 errors cannot be compared to a candidate native count; none is available. Native PCB render and required native checks remain blocked/pending.

Remaining review: exact native pad/courtyard and copper-edge checks; provisional bolt conflicts; physical testpoint probe approach and motor-connector body access; USB plug envelope; real mounted bodies; bottom-part height and shaft/magnet/bolt grip/gap in 3D. 2D geometry does not solve the motor gap. No fabrication, fit, assembly or physical-test claim is made.

## Locality measurements in stable snapshot

Status FET pulldowns are 2.08–2.15 mm center-to-center from their FETs; status gate resistors are 1.17–2.25 mm. Buzzer pulldown is 3.00 mm and gate resistor 3.22 mm from Q_BUZZER, so the buzzer network still needs closer electrical/layout review. MCU-to-crystal center distance is 7.13 mm; this is not a routed trace length and does not validate clock quality. Soft locality constraints do not guarantee electrically optimal placement.

Remaining provisional bolt rectangle intrusions: D_PD 0.1521 mm, L_BUCK 0.2613 mm, C_BUCK_IN 0.0879 mm. Worst pair constraint residuals include J_PD/L_BUCK 0.2489 mm, MCU/encoder-adjacent bypass capacitors about 0.227 mm, and J_PD/U_FLASH about 0.204 mm. Further rotation/cluster adjustment is needed. Native checks and real package polygons are required before interpreting these conservative bounds.

placement-stable.json and config/placement.json contain the same snapshot. Later scratch optimizer outputs are not the reported deliverable; measurement and hash files refer to the stable snapshot only.

## Fresh native build now available (supersedes blocked-output status above)

After source/config review and one unsuccessful old-session outcome poll, one authorized attempt of the same ordinary native workflow completed. Inputs were unchanged before/after (native-retry-input-before.sha256 matches native-retry-input-after.sha256). Full log: native-build-stable.log. Native output: dist/index/circuit.json, dist/index/pcb.svg, dist/index/pcb.png. Native render was inspected. No additional checks have been run.

Build exit 1: 35 top-level PCB errors remain, versus baseline 143. Breakdown: 8 footprint overlap, 17 courtyard overlap, 6 placement and 4 outside-board findings. There are zero standalone pad-clearance records, but grouped footprint errors still contain pad-clearance violations; do not interpret this as zero pad-clearance failures. Both outputs contain 99 source/PCB components and 89 CAD components. Candidate has zero PCB traces and zero vias.

Specific native blockers: two fixed USB courtyards remain 0.25 mm beyond edge; C_IO33/C_IO42 copper clearance is 0.243 mm rather than required 0.250 mm and their courtyards extend approximately 0.01 mm outside. L_BUCK copper intersects the bolt keepout. D_PD, L_BUCK and C_BUCK_IN courtyards intersect bolt keepouts. Through-hole conflicts include J_PD/L_BUCK, J_DATA with C_BUCK_OUT2, R_CC1 and C_VM_SENSE, and J_MOTOR with R_REF_L and C_TEMP. MCU/bypass and buck cluster courtyard conflicts remain. Exact serialized findings are in native-stable-findings.json.

This is a measured improvement, not a passing layout, manufacturable design, assembly approval or completed motor-gap solution. Native rendering also exposes crowded silkscreen; no label-placement or imported footprint edits were performed.
