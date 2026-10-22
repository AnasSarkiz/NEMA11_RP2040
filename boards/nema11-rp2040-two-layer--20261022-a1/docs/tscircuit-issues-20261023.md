# tscircuit upgrade and issue review — 2026-10-23

Revision `0.6.2-issues-review-wip`, same existing package
`AnasSarkiz/NEMA11_RP2040_Compact_Prototype`.
Comparison baseline: Git `b96bc2b158cee0256459a1a03d8df38c7f5c18af`.
This is an unrouted prototype review, not fabrication approval.

## Upgrade and fresh imports

The actual `tsci upgrade` command succeeded and installed tscircuit **0.0.3005**.
Local dependencies are pinned to **CLI 0.1.2401 / tscircuit 0.0.3005**;
`bun install --network-concurrency 1 --prefer-offline` succeeded with integrity
verification enabled. Version and npm integrity evidence is in
[checks/20261023](../checks/20261023/upgrade-status.json).

All **47 unique JLCPCB imports succeeded**, including the excluded GCT connector.
All 141 produced TSX/OBJ/STEP files were promoted unchanged. Only C5815189's TSX
changed relative to the baseline; all 94 model files are byte-identical. Every
manufacturer identity, pin label, passive value and electrical pad mapping
matches the baseline (allowing a uniform footprint-origin translation).
These comparisons establish integrity, not datasheet, stock or assembly approval.
See [comparison.json](../checks/20261023/comparison.json) and
[fresh-imports.json](../checks/20261023/fresh-imports.json).

## Findings

| ID  | Finding and scope                                                                       | Current disposition                                                                  |
| --- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| T01 | C5815189 USB4145 locator slot differs from manufacturer drawing.                        | Blocking component acceptance; supplier/importer responsibility unconfirmed.         |
| T02 | Default multi-sheet CLI SVG export includes only the first sheet.                       | Reproduced; explicit official per-sheet renderer used for review exports.            |
| T03 | Untouched C99269/C458749 symbol defaults fail the CLI's internal label-clearance check. | Reproduced in isolated native-import fixture; imported definitions remain untouched. |
| T04 | `check schematic-placement` reports findings but returns exit code 0.                   | Reproduced; additional strict report gate fails on findings.                         |
| T05 | Upgrade command can return 0 after child installer failure.                             | Runtime reproduction on CLI 0.1.2400; identical failure handler remains in 0.1.2401. |
| T06 | `is_connected` is false for pins with directly attached matching net labels.            | 29 observed metadata discrepancies; source and schematic geometry are connected.     |

Additional import-metadata limitations are recorded under T07 below; these
warnings are not automatically treated as proven tool defects.

No issue was posted or message sent to upstream maintainers. The fixtures and
raw outputs below make these findings reviewable without modifying dependencies.

### T01 — GCT C5815189 slot: pinching fixed, width still wrong

[GCT drawing, page 2](GCT-USB4145-drawing.pdf) specifies **one round Ø0.71 mm hole
and one horizontal 1.01 × 0.71 mm slot**, centers 8 mm apart, with ±0.05 mm drawing
tolerance. The earlier interpretation of two circular holes was incorrect.

The former CLI 0.1.2400 import produced an approximately 0.80 × 0.71 mm
inward-pinched polygon. The fresh CLI 0.1.2401 import now produces a rounded
polygon approximately **1.510 × 0.710 mm**, with correct 8 mm pitch. It contains
the minimum slot interior; the earlier pinching is no longer reproduced.
However, the slot is **0.50 mm wider** than the 1.01 mm drawing dimension.

The [geometry report](../checks/20261023/usb-locator.json) fails the manufacturer
comparison. The [native fixture](../checks/20261023/usb-locator-repro.circuit.tsx)
builds successfully and preserves that geometry in
[its native JSON](../dist/checks/20261023/usb-locator-repro/circuit.json).
A successful native build does not establish manufacturer agreement.

An independent raw EasyEDA request returned HTTP 403
([status](../checks/20261023/raw-supplier-fetch-status.json)); therefore the
underlying supplier footprint was not independently compared. This is a
confirmed import-output discrepancy, **not a proven importer-only defect**.
C5815189 remains excluded; its footprint/model pose is not patched. The selected
C165948 alternative still needs ratings, footprint, mating and stock approval.

Reproduce from this board directory:

```sh
tsci import --jlcpcb --download --use-exact-footprint C5815189
# Import into a fresh output directory; do not overwrite reviewed assets blindly.
tsci build checks/20261023/usb-locator-repro.circuit.tsx --pcb-png --pcb-svgs
python3 scripts/check_usb_locator_holes.py imports/USB4145_03_0070_C/USB4145_03_0070_C.tsx --output checks/20261023/usb-locator.json
```

The supported full-refresh script imports into ignored candidate directories:
`python3 scripts/refresh_components.py --evidence-dir checks/20261023`.
It records original import commands, exit codes and produced assets.

### T02 — later A4 sheets absent from default SVG export

[Two-sheet fixture](../checks/20261023/multi-sheet-repro.circuit.tsx) uses two
untouched imported resistors on separate native A4 sheets. Run:

```sh
tsci build checks/20261023/multi-sheet-repro.circuit.tsx --schematic-svgs
```

Exit is 0. Native JSON contains two sheets, but the only generated schematic SVG
contains `R_FIRST`, not `R_SECOND`.
[Measured result](../checks/20261023/multi-sheet-export-check.json).
Treat this as an export limitation; the command alone does not prove all sheets
were exported. The official `convertCircuitJsonToSchematicSvg` API accepts
`schematicSheetId`. Our [export script](../scripts/export_a4_schematics.mjs)
uses that API for all six board sheets and checks complete component coverage.

### T03 — native imported symbol labels violate native clearance rule

```sh
tsci check schematic-placement checks/20261023/imported-symbol-labels-repro.circuit.tsx
```

[Fixture](../checks/20261023/imported-symbol-labels-repro.circuit.tsx) separates
C99269 TMP102 and C458749 RGB LED and supplies no symbol-size overrides.
The check reports `SchematicBoxInnerLabelCollision` inside both default symbols:
TMP102 ALERT/V_POS gap 0.05 vs required 0.10 schematic units; RGB pin-label gaps
0.05 and 0.028 vs required 0.10.
[Raw output](../checks/20261023/imported-symbol-labels-repro.txt).
The checker suggests wider symbols; the project's import-only policy prohibits
patching those definitions. Symbol acceptance remains blocked.

### T04 — zero command exit does not mean schematic findings are absent

The required main-board command returns 0 while emitting **13 findings**:
2 internal symbol-label clearances, 1 diode/resistor alignment, 3 component/net
label collisions, 5 rail-component orientations and 2 capacitor grouping issues.
These are not waived. CLI command semantics may be advisory; this is an
important automation limitation even without assuming an unintended contract.

[check_schematic_findings.py](../scripts/check_schematic_findings.py) parses the
unchanged native report after the required CLI invocation and returns 1 for
findings or parse errors. [Strict gate result](../checks/20261023/strict-schematic-gate.json).
The strict gate adds enforcement; it does not replace any required check.

### T05 — failed installer status swallowed by upgrader

The real current upgrade succeeded. A controlled failure test invokes an
unmodified CLI with only the child package manager replaced by a stub that
returns 42. No actual dependency installation is performed during this test.

On cached CLI 0.1.2400, the child installer was called and failed with 42; the
CLI printed an update failure and nevertheless exited **0**.
[Runtime evidence](../checks/20261023/upgrade-controlled-failure-previous-release.json).
The extracted `updateTsci` failure-handler function is byte-identical in current
CLI 0.1.2401: the catch prints the error but does not propagate failure status.
[Source comparison](../checks/20261023/upgrade-failure-handling-source.json).

Current 0.1.2401 is already latest and correctly skips installation in the
negative control; no unnecessary-reinstall bug was reproduced. The failure path
was exercised on 0.1.2400, not on a failed real 0.1.2401 installation.
[Reproduction harness](../scripts/reproduce_upgrade_exit.py).

### T06 — net-label attachment absent from `is_connected` flag

In unchanged native board JSON, 29 schematic pins have `is_connected: false`
while a same-sheet, same-net label anchor exactly touches the pin. Examples:
R_PD_CFG pin 2/GND, C_PD pin 2/GND and L_BUCK pin 2/V3V3.

[verify_schematic_ports.py](../scripts/verify_schematic_ports.py) independently
checks logical source nets plus matching wire segments or label anchors at each
pin. **296 non-NC ports pass; 36 explicitly unused ports remain NC; no attachment
failures are found.** [Detailed result](../checks/20261023/schematic-port-connectivity.json)
lists all 29 discrepancies and label IDs. A flag-only consumer would report
false opens. This finding does not prove schematic absence of unintended shorts,
PCB routing, or datasheet correctness. Native JSON flags were not edited.

### T07 — connector/part semantics incomplete in imports

The [unchanged native build log](../checks/20261023/native-build.txt) reports
31 pin-role warnings plus reference-prefix and connector access warnings.
USB/JST connectors, the crystal and transistors are imported as generic `chip`
wrappers, producing reference-prefix warnings; several definitions omit semantic
`pinAttributes`. This limits the strength of semantic ERC, even though physical
pin numbers and logical nets remain present.

J_PD, J_DATA (C165948) and J_MOTOR (C131334) lack explicit footprint
`insertionDirection`. The native checker infers directions that disagree with
its expected board-edge access directions. This is an import-metadata and
assembly-review blocker, not proof that an inferred direction matches the actual
mating face. Genuine supplier drawings/models and the mating plug must resolve
it; imported footprints are not patched to silence the warning.

The same log emits availability uncertainty, including C45783, C52923 and C1525.
Those warnings are not a current inventory count or a guarantee of no stock.
Full BOM availability remains unapproved; no stock is reserved.

## Other failures and limits

- Current native board build fails with **157 layout records**: 60 footprint
  overlaps, 56 courtyard overlaps, 29 placement, 10 pad clearance and 2 components
  outside the outline. These are board-design failures, not established tool
  defects. C_BULK extends 0.289 mm and D_STATUS 0.142 mm beyond native board bounds.
- Former internal autorouter exceptions are absent in all five required checks
  under this version. Routing remains disabled by the validation gate.
- Historical large combined registry archives/per-file asset uploads failed;
  bounded uploads using the official CLI archive API previously succeeded.
  Those historical errors were not freshly reproduced as a current CLI defect.
- Network HTTP 503 responses and the raw-supplier HTTP 403 are recorded as access
  failures, not attributed to a token or to tscircuit source code.
- The installed Inkscape converter rendered transparent SVG fills black; that
  PDF was rejected. Headless Chromium timed out. Resvg rendered the unchanged
  SVGs correctly. These are converter/environment observations, not established
  tscircuit bugs.

## Continued board work

The [six-page A4 PDF](../artifacts/20261023/NEMA11-schematics-A4-WIP.pdf) covers
all **92 components / 332 ports**, including the optional encoder DNP sheet.
It embeds 300 dpi renders; unchanged vector SVGs are supplied separately.
Page dimensions and coverage are measured in
[a4-pdf-export.json](../checks/20261023/a4-pdf-export.json). The contact sheet and
MCU sheet were inspected: black-fill conversion is resolved, while crowded
labels and native placement findings still prevent readability approval.

No imported definition, pin map, footprint or CAD pose was manually changed.
The board remains two-layer, top/bottom assembly, buzzer fitted, routing disabled.
Rear motor-bolt dimensions and bottom clearance, manufacturer/stock/mating review,
thermal qualification, routing/shorts, CAM and physical testing remain open.
