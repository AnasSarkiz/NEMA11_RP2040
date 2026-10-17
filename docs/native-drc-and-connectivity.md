# Zero-error DRC and complete physical pin connectivity

The checked controller PCB reports **zero native DRC errors, zero physical opens
and zero shorts**. The result applies to the exact board hash recorded in each
artifact. Clearance rules, circular mounting keepouts and all electrical copper
remain in force. The PCB geometry is unchanged from the preceding routed milestone.

## Native geometry correction

The frozen `@tscircuit/checks@0.0.242` trace checker measures a trace's distance to
a circular keepout against its bounding rectangle. This creates 36 false errors
on this PCB. The same fallback remains in the inspected 0.0.256 release. Native
pad/via checks already use the true circle; the defect is in the trace fallback.

`tools/pcb/patches/circle-keepout-clearance.json` corrects only that distance branch
in the frozen library and CLI bundle. It projects the circle center onto the
finite segment, clamps the projection to its endpoints, then subtracts the circle
radius and half the full trace width. All original thresholds, layer checks,
exclusions, warning policy and error generation remain unchanged. No findings
are filtered, reclassified or waived. The three reviewed exposed-pad ground vias
retain their separately documented filled-and-capped manufacturing requirement.

`scripts/apply_native_keepout_fix.py` verifies the pristine SHA-256 before applying
the exact patch, or verifies the corrected SHA-256 when already applied. Unknown
bytes fail. Setup and CI apply it after frozen installation; the DRC runner also
requires the corrected hashes. The native report explicitly identifies this
corrected toolchain. Unpatched external tools may still show their circle-box bug;
this is not a claim that their behavior has changed.

Ten regression tests cover true circle clearance inside its bounding rectangle,
translated centers/radii, finite-segment endpoints, crossing/contained traces,
insufficient clearance, full trace width, rectangles, layers and advisory warnings.
The stock checker fails three circle-clearance cases; the corrected checker passes
all ten and still detects actual violations. Both run logs and the original
36-error board report are preserved beside the current zero-error report.

## Every physical pin is accounted for

`all-pin-connectivity.csv` and its JSON report enumerate all **341 pins on all
92 electrical components**. A global physical graph joins copper only when actual
metal intersects on the same layer. Real plated barrels join their declared
layers; symbolic net membership cannot bridge a gap or hide a foreign-net contact.

All **304 required pins** belong to their correct, single connected copper island
across **64 nets**. The other **37 pins are explicit intentional NCs**, including
unused MCU and connector pins. Each NC must retain its physical pad and remain
isolated. Connecting these pins merely to remove an NC designation would change
the reference circuit and is not part of this design.

The inventory distinguishes 81 fitted SMT components, one manually soldered PH
header, seven bare PCB test points and three optional encoder DNP components.
DNP footprint pins remain physically checked and routed according to the source.
Six additional fault tests prove that missing pads, disconnected same-name nets,
foreign-net shorts, NC contacts and disconnected DNP footprints are rejected.

Run with the frozen toolchain:

```sh
python3 scripts/apply_native_keepout_fix.py --check
bun test tests-native
bun scripts/check-controller-pcb.tsx --checks-only
python scripts/audit_controller_connectivity.py
python scripts/audit_controller_pcb.py
python scripts/review_controller_native_drc.py
```

Use the CAD Python environment for the Shapely scripts. Existing independent
copper/drill/edge, clock, USB ground-reference, all-trace, Gerber shorts and CAM
checks remain required. `verify_controller_milestone.py` verifies exact hashes
and now requires zero native errors as well as the all-pin report.

These digital checks do not establish factory process acceptance, harness crimp
qualification or measured current/thermal/regeneration performance. Those remain
in [manufacturing requirements](manufacturing-requirements.md).
