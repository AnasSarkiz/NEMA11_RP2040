# Full isolated board integration result

**Candidate is not integration-ready.** It removes both intended label findings, preserves the complete physical PCB and electrical graph, but adds one schematic path-spread finding. No production files or installed production dependencies changed.

## Frozen inputs and fresh output

- Board source SHA256: `864cd4929a056bd1c07dfc3345ce04ca563f01db223f340dbc6514da1fb1a045`.
- Frozen baseline native SHA256: `b93b921adc556e840dee2bc4acb0d4f2de8fe990ebf6b6a2638e4636379acf51` (4204 records).
- Fresh isolated patched-core native SHA256: `801a9b177e0b5f2988e635c4862695e5b94453cf5540d1cb2caa716b615244bc` (4213 records).
- Full copied dependency tree byte comparison found exactly one changed file: `@tscircuit/core/dist/index.js`. Original bytes were asserted against the studied 0.0.2304 artifact before applying the one-line candidate. Package manifests/locks were unchanged. `applied-hashes.json` records both hashes.
- The existing serialized milestone script produced a fresh-build receipt with unchanged source inputs, despite native build exit1. Native failed on the same two `pcb_component_outside_board_error` groups, with no nested details.

## Full-board schematic result

The exact unmodified CLI0.1.2446/analyzer0.0.83 and separate source replay agree:

- Frozen baseline: **3 findings** (two label clearances plus C_BOOTSTRAP orientation).
- Fresh patched-core native output: **2 findings**, C_BOOTSTRAP orientation plus new `RailPathTooSpreadOut` at U_BUCK.FB. Both label collisions are cleared. TMP102 and RGB boxes now both have width1.6.
- Same fresh JSON with separately labeled bootstrap analyzer candidate: **1 finding**, U_BUCK.FB path spread. This is NOT a zero-finding schematic.

The generic array-label correction changes12 chip-box widths. This recomputes schematic port positions and traces. U_BUCK width changes1.2→1.4; the newly reported visible FB-to-power path spans10.30 units (recommendation8) and has length12.90. Its exact route and issue are in `core-only-analysis.json`. This requires investigation or schematic placement work before integration; it was not hidden, suppressed or fixed by a board-local override. The desired3→1/3→0 result was therefore not achieved.

## Preserved physical and logical behavior

`native-comparison.json` compares every record type:

- **All pcb_* records exactly equal**, including native PCB error records. No copper/pad/hole/board geometry or layer change.
- **source_component, source_port, source_net and source_trace records exactly equal**. Physical pin identities, pin attributes and electrical connectivity graph are unchanged.
- **All cad_* records exactly equal**.
- Differences are schematic records, source filesystem hash, supplier availability warning records and seven new datasheet-timeout warnings. Availability warning count is85→89; dynamic IDs also differ. All seven added `source_property_ignored_warning` records disclose that datasheet metadata could not be fetched within5 seconds. These external-service differences remain visible; they are not normalized away or blamed on the core patch.
- Exact candidate pin checker on fresh native JSON returns **26 warnings** versus pristine30. Every one of those26 warning records exactly equals the frozen baseline candidate result. See `pin-candidate-replay.json`.

## Checks

- Format, TypeScript,23 prebuild tests,9 emitted contracts, source/import structural validation and conservative independent geometry audit pass.
- Native build remains exit1 on the two existing USB courtyard/board-boundary groups.
- Unmodified native pin checker still reports30 (candidate is only a separately labeled replay). Strict pin, source and schematic gates fail, as they should. Source check reports seven metadata-fetch timeout warnings.
- Native schematic/PCB export commands finish. SVG/PNG and native JSON evidence are included. No fresh visual acceptance claim is made solely from successful export.
- No full upstream core/checks/analyzer suite or upstream CI was run. Focused candidate regressions do not replace those. No routed PCB, manufacturing, thermal, mechanical hardware, or assembly approval is implied.

## Build review

The first invocation was stopped after an api.tscircuit.com review concern. Read-only verification established additional public manufacturer-part datasheet GETs beyond stock lookup. Original session was confirmed gone and milestone lock free before one normal retry. The retry completed without endpoint/check/configuration changes. `NETWORK-REVIEW.md` supersedes the earlier stock-only characterization and records the exact source paths and remaining runtime trace limitation.

## Reproduction and portable evidence

The archive omits installed dependencies, caches and duplicate supplier imports. `board/` preserves source/config/scripts/tests, fresh native outputs and selected logs/receipts; restore exact imported assets from the frozen board/import manifest for a full native build. Its package-lock remains the original dependency lock; apply the narrow core patch only to an isolated installed tree with original SHA checks. Do not install it into the working board based on this result.

For local analysis of the included fresh JSON:

    BASELINE=1 node --loader ./analyzer/validation/loader.mjs analyzer/replay.mjs board/dist/index/circuit.json core-only-analysis
    node --loader ./analyzer/validation/loader.mjs analyzer/replay.mjs board/dist/index/circuit.json core-and-bootstrap-analysis

These commands do not render a board or issue external requests. The second uses only the explicitly labeled bootstrap analyzer candidate. Main-board gates and files remain unchanged.

## U_BUCK.FB trace comparison and optional next step

`ubuck-fb-before-after.json` preserves the exact affected source/port/box records and trace endpoints. U_BUCK center stays(26,13.2); FB terminal moves from(25,13.4) to(24.9,13.4). Originally FB used a short automatic V3V3 power-label stub ending(24.699,13.651). Fresh rendering instead draws a long shared-V3V3 connection from R_PG terminal(14.5,15.8), through(14.5,16),(16.59,16),(16.59,13.4), to FB. Thus the new finding is driven by a wire-versus-rail-label routing choice, not only a0.1 difference in an existing long wire. R_PG and FB remain on exactly the same explicit power net.

A schematic-only U_BUCK horizontal move of+0.1 would restore the prior FB endpoint, but that does not prove the auto-label/routing choice will revert. Moving R_PG closer could affect its other functional schematic relationships. Neither proposal has been rendered or accepted; a source-controlled isolated placement trial and fresh render is required. No native JSON was edited to manufacture a clean result. The initial full patched output remains frozen.
