# Independent nominal assembly-spacing screen

No NEMA11 same-face body-spacing failure is supported by this review. The saved isolated candidate has 89 fitted CAD models, 16 top and 73 bottom. All 2,748 same-face pairs have whole-imported-model XY bounding-box clearance greater than 0.2 mm. Minimum is J_MOTOR–C_BULK, top, 0.524997 mm. Bottom minimum is R_PG–D_TVS, 0.548900 mm; next D_DATA–U_ESD 0.550025 mm, D_PD–R_BUZZER_PD 0.552000 mm and R_REF_L–U_TEMP 0.552808 mm. These are conservative nominal model lower bounds: whole-model boxes include leads, so they are not mislabeled body dimensions. The body subset cannot be closer than a containing whole-model box if the supplied model and pose are accurate.

This does not qualify real parts or establish a JLC acceptance rule for this board. The separate NEMA8 Y81 spacing rejection is useful context only. No original JLC rejected pairs or same-face basis were supplied, so its outcome cannot transfer to NEMA11.

## Inputs and method

Repository root: supplied by the required --repo argument.
Board root: boards/nema11-rp2040-two-layer--20261022-a1.
Candidate: references/electrical-placement-20261109/integrated.circuit.json; associated config integrated.placement.json in that directory. This remains an isolated saved candidate, not newly validated main.

The script reads each local OBJ vertex, subtracts authored model_origin_position, applies native rotations in z, y, x order, then adds native position. The ordering was independently checked against all 89 baseline official-loader bounds in docs/engineering-review-20261109/underside-envelope/official-loader-bounds.json, using references/reconstructed-placement-final/circuit.json: exact numerical agreement. The naive x, y, z order did not match; it was not used. Unsupported scale, fit and orientation fields are rejected. Each pair is filtered by actual PCB side; DNP records have no fitted CAD and are excluded. XY axis-aligned bounds contain the whole supplied mesh and therefore provide conservative minimum-distance bounds. No mesh/body segmentation, silhouette, manufacturer maximum dimension or tolerance validation was performed.

## Visual review and geometry distinctions

Inspected existing PCB renders artifacts/20261108-reconstruction/pcb/top.png and bottom.png under board root. These are baseline PCB drawings, not an assembly photograph or saved candidate 3D render. Bottom labels are mirrored and crowded; they should not be interpreted as body collisions. The top image visibly places driver on top and MCU/encoder on bottom in the respective views. Connector off-board errors are explicitly present and are a separate concern, not a same-face model collision.

Generated and inspected model-xy-screen.png from candidate model bounds, with separate top/bottom panels in top-view XY coordinates. It is clearly labeled an analytic plot, not a native render. No board-specific assembly photograph or candidate 3D screenshot was found in the supplied board directory.

Courtyard AABB screening, also same-side and fitted-only, yields 106 pairs below 0.2 mm but no overlapping AABBs. Courtyards already include package/process margins and cannot be compared with a body-to-body threshold as though they were bare bodies. The existing PCB geometry audit measures copper at a different 0.15 mm threshold and includes DNP copper; its passing status is not a body-spacing certificate. Conversely, closely spaced courtyard edges do not contradict the >0.52 mm whole-model gap.

Most useful physical assembly verification targets are the closest nominal pairs above, supplier model/package accuracy, and through-hole projections. Opposite-face body overlaps were deliberately excluded from same-face spacing. Through-hole pins may emerge on the opposite face, so a complete 3D assembly review must separately check those intrusions, solder and motor/fastener clearance.

No native build, dependency installation, network, source/import changes, routing or publication occurred. All output is outside the repo. Existing native errors and manufacturing blockers remain unaffected.

## Portable reproduction

Requires existing Python, NumPy and Matplotlib; the script does not install anything.

    python review.py --repo /path/to/nema11_reconstructed --output /path/to/output
    python -m unittest discover -s . -p 'test_review.py' -v

`--repo` is mandatory; `--output` defaults to the script directory. Unsupported model transformations are rejected before their vertices are transformed. The official baseline must contain exactly the same 89 unique component names, and the script fails if neither supported transform order reproduces it. Candidate names must match too. Five tests cover axis and diagonal AABB gaps, overlap, same-face filtering and unsupported transforms. `portability-validation.json` records the intentional conversion of input metadata to a repository-relative path. Numerical rows/pairs, courtyard JSON and image remain unchanged. The original absolute-path metadata is retained only in the prior reproduction directory. The prior script is preserved as `review-original.py` for provenance only.
