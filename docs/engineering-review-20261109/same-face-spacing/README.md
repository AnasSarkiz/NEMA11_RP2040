# NEMA11 same-face nominal model spacing

Reviewed 2026-11-09 UTC. No same-face component-body spacing failure is
demonstrated by the saved candidate's imported models. This is an offline
screen of an existing native snapshot, not a new native build or assembly
approval. Current source placement coordinates match that saved candidate.

## Result

All 2,748 same-face pairs among 89 fitted components have conservative nominal
whole-model XY clearance greater than 0.2 mm. There are 16 fitted parts on top
and 73 on bottom. Ten DNP components are excluded from this assembly screen.
Their copper remains relevant to the separate PCB geometry checks.

Closest pairs:

| Pair | Face | Nominal whole-model gap |
| --- | --- | ---: |
| J_MOTOR and C_BULK | Top | 0.524997 mm |
| R_PG and D_TVS | Bottom | 0.548900 mm |
| D_DATA and U_ESD | Bottom | 0.550025 mm |
| D_PD and R_BUZZER_PD | Bottom | 0.552000 mm |
| R_REF_L and U_TEMP | Bottom | 0.552808 mm |

The same-face count excludes all 1,168 opposite-face pairs. Forty-six of those
opposite-face pairs have overlapping projected convex hulls; that alone is
not a physical collision because they occupy different board faces. Pins or
shell stakes that cross the board require a separate three-dimensional check.

An independent axis-aligned bounding-box calculation agrees with the closest
pairs. Its courtyard screen finds 106 fitted same-face courtyard pairs closer
than 0.2 mm, but no courtyard overlap. Courtyards include package/process
margins, so their edge gap cannot be substituted for a bare-body gap. The
minimum courtyard gap, approximately 0.001 mm between R_DM and C_BUZZER, does
not contradict their much larger nominal model separation.

## What the result does and does not mean

The motivating precedent was a separate NEMA8 Y81 JLC review reported to have
required at least 0.2 mm part spacing and rejected the submitted spacing.
The rejected pairs and the review's side basis were not supplied here. That
outcome cannot be transferred to this NEMA11 layout.

This calculation uses complete supplier OBJ meshes, including leads and
shells, not a guessed plastic-body outline. A containing whole-model convex
hull or bounding box gives a conservative lower bound for the body subset
of that same nominal model. Neither calculation establishes that the supplier
model matches the maximum dimensions of the exact delivered part.

Not included: manufacturing tolerances, supplier model/origin errors, solder,
pick-and-place access, nozzle clearance, optional DNP population, through-hole
intrusions onto the opposite face, connector mating/strain relief, motor
geometry, fastener tolerances, panel rails or manufacturer acceptance.
The separate 2.5 mm body-to-edge and 5 mm rail guidance has not been resolved
for the intended panel or overhanging USB connectors. No placement was changed
to satisfy an assumed rule.

Existing top/bottom PCB images were inspected. They show the historical
7da9556 checkpoint, not the latest candidate assembly. Crowded or mirrored
labels and opposite-face outlines are not body-collision evidence.
`independent-aabb/model-xy-screen.png` is a newly generated analytic plot of
the saved candidate, explicitly labeled as model bounds rather than a native
assembly render. Both panels use top-view XY coordinates.

## Inputs and method

- Saved candidate native SHA-256:
  `f590d22ad18feff381969d4dfc4032eb65f51c80465a360de8063ea7953ab538`.
- Baseline native SHA-256:
  `b93b921adc556e840dee2bc4acb0d4f2de8fe990ebf6b6a2638e4636379acf51`.
- The independent analytic transform agrees with all 89 archived official
  `loadCadComponentMesh` bounds to less than 1e-8 mm. These official bounds
  were recorded previously; the loader was not rerun for this study.
- The script rejects unsupported scale, box-fit, normal axes or X/Y rotation,
  reads only local genuine OBJ files, and leaves native JSON unchanged.
- Each model is projected to its convex hull. Separating-axis and
  point-to-segment calculations measure conservative distances. The full
  pair set is filtered by actual PCB face before threshold screening.
- Seven focused regressions cover hull construction, separation, overlap,
  crossing edges, face filtering, authored origins and unsupported transforms.

From the repository root, using Python 3 standard library only:

```sh
B=boards/nema11-rp2040-two-layer--20261022-a1
S=docs/engineering-review-20261109
python3 "$S/same-face-spacing/audit_spacing.py" \
  --board "$B" \
  --native "$B/references/electrical-placement-20261109/integrated.circuit.json" \
  --baseline "$S/electrical-placement/inputs/board/dist/index/circuit.json" \
  --official "$S/underside-envelope/official-loader-bounds.json" \
  --output /tmp/nema11-spacing-replay.json
cmp "$S/same-face-spacing/spacing-report.json" /tmp/nema11-spacing-replay.json
python3 -m unittest discover -s "$S/same-face-spacing" -p test_spacing.py -v
```

The independent AABB/plot replay additionally uses NumPy and Matplotlib;
see its report for the command. No dependency install, native rebuild,
external validation request, routing or publication occurred in this review.
Main native verification remains paused and the board remains unrouted and
not fabrication-ready.

## Restore correction

During a fresh restore of cf0f661, the electrical placement study's baseline
input was found absent from the tracked working tree because its nested
`dist/` path was ignored. The exact file was recovered from verified Git
checkpoint 7da9556 and its existing declared SHA-256 matched. It is now
explicitly tracked. All 27 electrical-study checksums pass, and all seven
numerical output artifacts replay byte-identically. No historical circuit
bytes or placement results were changed by this backup-portability fix.
