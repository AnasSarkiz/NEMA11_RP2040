# New native-verified placement candidate, still WIP

Use placement.json from this folder only. This portable folder contains final placement/native evidence, not a schematic-source checkout. The original isolated study had a separate source copy that must not replace the main project schematic. No main edits, imported-definition edits, commits or publication were performed.

## Native build result

Fresh ordinary tsci build completed with exit 1 because two findings remain: J_PD and J_DATA courtyards each extend 0.25 mm outside the board. Their frozen edge-facing anchors were preserved; no exemption or error suppression was added. The native checks report no footprint overlap, courtyard overlap, pad clearance, copper-edge or bolt-keepout errors. There are also no nested related_errors. This is not a complete passing build.

Native finding progression: reconstruction baseline 143; preserved stable35 35; targeted candidates 18, 14, 9, 3, then 2. The original isolated study retained stable35 and targeted1 through targeted4 snapshots. Those intermediate study directories are not included in this portable final-evidence folder and are not needed to reproduce its independent audit. Included final log: native-build.txt. Included final native output: circuit.json, pcb.svg and pcb.png, all directly in this folder. Source and placement hashes match before/after the final run.

## Independent read-only geometry audit

independent-geometry-audit.json includes all actual emitted pads, polygon pad bounds, rotated plated-hole slots, motor circular annuli and DNP encoder copper. Conservative bounding-box minima:

- Between different-component, same-layer copper: 0.160 mm (required 0.150 mm).
- DNP-inclusive copper minimum: 0.160 mm.
- Copper to board edge: 0.361 mm (required 0.250 mm).
- Pad/courtyard bounds to provisional R2.35 bolt-head envelopes: 0.0445 mm.

No conservative pad pair falls below 0.15 mm. These are lower-bound geometric estimates, not fabrication tolerances or a 3D fit qualification. The very small bolt-envelope margin depends on the unverified provisional head envelope.

## Preservation and limits

All 99 source/PCB components remain; fitted population is unchanged at 16 top / 73 bottom. Frozen USB, motor connector, bulk capacitor, driver, ESD pair and centered encoder anchors are unchanged. PCB remains 28 × 28 × 1.6 mm, two layers, with original four mounting axes/holes. Zero traces and vias. Rotation changes only adjust placement of approved components, without editing footprints, symbols, pin maps or CAD.

The native preview was inspected. Silkscreen is still crowded and overlapping, so this is not yet the neat NEMA14-style presentation requested. Native PCB collision clearance does not validate USB plug approach, motor connector body/cable clearance, test-probe/tool access, motor-side part height, insulation, rear bolt grip/engagement, shaft/magnet alignment or actual motor-to-PCB gap. Those need explicit mechanical/3D and physical checks. No all-top assembly or fabrication-readiness claim is made. Routing remains disabled.

## Local electrical placement review still needed

Pulldown-to-FET center distances are 2.09 mm for buzzer and 1.65 / 2.59 / 1.89 mm for status R/G/B. Gate-resistor-to-FET centers are 3.95 mm for buzzer and 1.71 / 2.15 / 1.85 mm for status R/G/B. MCU-to-crystal center distance is 7.84 mm; centers are not actual pin-to-pin trace lengths. Clock loop, bypass-pin locality, buck hot-loop and driver-current return paths must be reviewed before routing. These distances are disclosed rather than claimed electrically optimal.

## Independent audit rotation correction

Parent review identified that the first independent audit handled rotated plated slots but not rotated SMT pills. This omission has been corrected. The installed circuit-to-svg renderer explicitly sizes rotated_rect and rotated_pill in local coordinates and applies a centered ccw_rotation transform; core also passes the pill dimensions with ccwRotationDegrees. Therefore the audit now derives world-axis bounds using absolute sine/cosine for both rotated SMT shape types, in addition to plated holes. Polygon coordinates remain already emitted world coordinates. Unknown SMT shapes fail the audit rather than being silently accepted.

The final native JSON contains 40 rotated SMT pills: 28 at 270°, four at 90° and eight at 180°. All are included in the corrected audit. Regression assertion for U_DRV pcb_smtpad_201 confirms world bounds of 0.2800096 mm in X and 0.8999982 mm in Y, rather than the unswapped dimensions. The corrected audit rerun finds no new violation and leaves the reported global clearance minima unchanged. Its log, script and machine-readable report are included. No candidate, native JSON or import was modified for this correction.

## Portable audit and regressions

The reusable checker is scripts/audit_placement_geometry.py. Defaults resolve from the board directory, independent of shell working directory: dist/index/circuit.json, config/placement.json and references/reconstructed-placement-final/baseline.placement.json. Override with --circuit, --placement and --baseline; --output writes a JSON report. Exit 0 means only that this conservative independent geometry scope passes, not that the native build or mechanical design passes. Native findings remain visible and unwaived in the report.

Reproduce this historical native evidence from the board directory:

    python3 scripts/audit_placement_geometry.py --circuit references/reconstructed-placement-final/circuit.json --placement references/reconstructed-placement-final/placement.json --output references/reconstructed-placement-final/independent-geometry-audit.json

Run regressions with:

    python3 -m unittest discover -s tests -p test_placement_geometry.py -v

Eight tests cover quarter-turn/general-angle SMT bounds, plated slot outer annuli, circular outer annuli, emitted polygon coordinates, invalid/unknown shapes, and DNP inclusion (including an intentionally colliding DNP pad in an in-memory test copy). The original corrected standalone checker/report/log are retained as original-corrected-audit.*; their historical paths are not the portable interface. No native circuit JSON was modified for these tests. The audit does not compare net connectivity or qualify manufacturing tolerances, electrical loops, probe access or 3D fit.

## Artifact path clarification

The historical standalone original-corrected-audit.py/log and native hash records retain paths from the isolated study (best-native/ and dist/index/). They are provenance records, not paths expected in this portable folder. Current files here are placement.json, circuit.json, pcb.svg, pcb.png, native-build.txt, baseline.placement.json and the audit evidence named above. Use the portable board script and explicit reproduction command above, not the historical standalone script. output-sha256.txt and checkpoint-hashes.json describe the files actually included here.
