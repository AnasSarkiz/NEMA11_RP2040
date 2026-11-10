# Opposite-edge USB placement study, 2026-11-10

**No candidate in this study is adopted. Active placement is unchanged.**
The user requested USB-C ports on opposite sides, with a motor assembly. This
study covers USB placement only. It does not qualify the separate assembly
preview, authorize routing, waive a boundary error, or establish fabrication fit.

## Outcome

Both north/south and east/west arrangements were screened using rigid transforms
of the genuine native copper and courtyards, including through-hole shell tabs
on **both** layers. A direct connector move is not safe. A bounded broader
re-layout also did not produce a candidate passing the conservative constraints.
This is a failed search, not a proof that no layout exists.

| Recorded candidate | Copper AABB pairs below 0.15 mm | Minimum provisional screw-envelope gap |
| --- | ---: | ---: |
| DATA south, PD unchanged north | 40 | 0.07500 mm |
| PD west, DATA unchanged east | 23 | 0.07500 mm |
| South DATA plus repacked top components | 33 | 0.05493 mm |
| West PD at Y=3.95, buzzer north, MCU down 0.10 | 13 | 0.00793 mm |
| Broader west-PD re-layout, best of eight starts | 2 | **−0.07685 mm** |
| Broader west-PD re-layout, MCU constrained right, intermediate | 11 | **−0.17733 mm** |
| Broader west-PD re-layout, MCU constrained right, final | 18 | **−0.04301 mm** |

AABB pair flags are conservative obstacles, not exact-shape copper DRC. None is
waived merely because the bounds are conservative. The best broad-search
candidate still has two PD shell-tab/R_STATUS_R pad flags and an MCU courtyard
intruding into the southwest screw envelope. It must not replace the active
placement. Even the old positive ~0.075 mm margin is nominal and not a qualified
fastener, assembly or tolerance allowance.

The north/south trial places DATA at (0, −8.65), rotation 0. Its genuine courtyard
then spans X ±5.1751108 and Y −14.250021…−5.5758692. The direct move conflicts with
motor-header/bulk/driver circuitry and also with bottom-side MCU, oscillator and
temperature circuitry through the connector shell tabs. The top-only repack
moves the motor header east and bulk west, but fails the full two-layer screen.

The east/west alternative preserves DATA, its ESD/protection neighborhood, the
motor header, bulk capacitor and driver. PD at (−8.65, 3.8), rotation 270, avoids
some bottom circuitry at the cost of a tighter northwest fastener envelope.
The broader search allowed coordinated bottom-side circuitry and buzzer/status
moves, with weighted relative-position preservation for the MCU/decoupling/
oscillator cluster and the PD/support cluster. Those weights are heuristics,
not electrical qualification. A future successful geometric candidate still
requires power-loop review, MCU decoupling/oscillator review, PD bypass and data
signal/return-path review, native rebuild, and mechanical mating review.

## Reproduction and evidence

Run from repository root (Python standard library only):

```sh
python docs/engineering-review-20261110/opposite-usb/audit.py
python -m unittest discover -s docs/engineering-review-20261110/opposite-usb -p test_audit.py -v
```

Nine regression tests cover saved-result reproduction, all candidates remaining
rejected, no mutation, identity and quarter-turn round-trip transforms, source
population and mounting axes, unknown components, invalid rotations, nonfinite
coordinates and unsupported layer changes.

`baseline-geometry.json` is an explicitly labeled historical subset of the
native circuit at repository commit `b62ede0458f966e10c06d4f611e91b529ee5541c`.
It includes source/component identities, PCB outline, copper, courtyards and
four keepouts, plus the active placement at that point. It is **not** a native
circuit or a regenerated board. Original native file SHA-256:
`37e2f0f8123048bf3c87dbaed27447afeeebb32125d14c78fac18f444e827903`.

The fixture keeps this counterfactual study reproducible after later native
builds. `candidates.json` records every reported pose, including rejected
poses. `results.json` records input hashes. Supplier imports, connections,
28×28 mm board, mounting axes at (±11.5, ±11.5), 2.7 mm holes and R2.35 provisional
screw envelope were not modified. Historical anchor references remain historical.

`search.py` retains the optional eight-start broad-search algorithm. It requires
NumPy/SciPy (used here: NumPy 2.3.5, SciPy 1.17.0); results can vary by platform.
It only writes a candidate if `--output PATH` is explicitly passed, and never
writes active board inputs. Recorded rejection evidence does not need those
packages. The objective uses 0.17 mm copper, 0.08 mm courtyard, 0.10 mm board-edge
and R2.45 screw targets; existing fixed anchors may already miss the extra
search margin. Independent `audit.py` uses the unchanged baseline audit and
reports real R2.35-envelope gaps rather than accepting the objective score.
The follow-on bounded rightward-MCU search (`--mcu-right`) uses three starts and constrains MCU
X translation to +0.8…+2.5 mm; it likewise did not produce a valid candidate.

## Unresolved physical checks

The flat TYPE-C-31-M-12 nominal mating face remains flush at the selected board
edge under the existing model registration interpretation. Its courtyard still
extends about 0.250021 mm outward; no shrink, recess or off-board exception was
used. See the sibling `usb-edge-boundary` study for the supplier drawing and
registration limits. The transforms do not evaluate CAD solids, plug/overmold,
panel rails, solder protrusion, motor hardware, tolerance stack or assembly
sequence. These remain required even if a future candidate clears this screen.
