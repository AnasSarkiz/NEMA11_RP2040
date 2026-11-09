# NEMA11 pin metadata and automatic label sizing investigation

## Result

Three generic tool defects are reproduced. Candidate changes remain isolated here, unpublished and not installed in the board. The board source, imports, dependency files, native JSON, diagnostics and constraints were not edited.

1. `@tscircuit/checks@0.0.270` does not count `is_passive`, `is_input`, `is_output`, or `is_bidirectional` as pin attributes in its underspecification check, despite all four being defined by installed circuit-json's SourcePinAttributes schema. Consequently fully specified passive pins can be called wholly unspecified.
2. Its no-ground check omits the explicit all-connectable-pins-passive exception already used by its no-power check. A fully passive connector therefore gets a chip-ground warning even when none of its pins require ground. The candidate mirrors the existing power rule, based only on typed attributes. It does not assume passivity from names, symbols, part numbers or topology.
3. `@tscircuit/core@0.0.2304` automatic box sizing counts the number of aliases rather than displayed label characters for array-valued labels. This is the cause of the two reported TMP102/RGB inner-label clearance failures. A one-expression change reuses the existing displayed-label-width helper. No imported `schWidth` or board override is introduced.

## Exact checks and results

- Checks owner: https://github.com/tscircuit/checks, source paths recovered verbatim from installed 0.0.270 source map under `upstream/lib/`. Core owner: https://github.com/tscircuit/core, `lib/utils/schematic/getAllDimensionsForSchematicBox.ts`. CLI owner: https://github.com/tscircuit/cli.
- Installed CLI 0.1.2446 imports `runAllPinSpecificationChecks` from the installed checks package. Directly running that package on the immutable copied emitted JSON reproduces all 30 warnings, 0 errors.
- Candidate returns 26 warnings: 6 unspecified, 10 no-power, 10 no-ground. Exactly four warnings disappear: underspecified and no-ground for Y_MCU and J_MOTOR. Every remaining warning record is byte-for-byte equivalent as a JSON value to the original output.
- Pin regression suite: 10/10 pass on candidate. Same assertions against pristine 0.0.270 fail (including all four attribute types, passive handling and board count), confirming regression sensitivity.
- Core regression suite: 5/5 pass on candidate. Same assertions fail on pristine core for the two imported label sets and hidden-alias size invariance. Explicit width remains respected; ordinary string labels retain existing size.
- Actual `Circuit.renderUntilSettled()` results: U_TEMP array labels 1.2 x 0.8 originally versus 1.6 x 0.8 patched; D_STATUS array labels 1.2 x 0.6 originally versus 1.6 x 0.6 patched. The identical labels represented as strings already yield width 1.6 on pristine core.
- Direct unmodified 0.0.83 `SchematicBoxInnerLabelCollisionSolver` reproduces suggested widths 1.289 and 1.272 for original alias-array fixtures. Both candidate fixtures have zero inner-label collisions. Analyzer gap remains 0.1 and renderer-based text metrics remain unchanged.

The analyzer embedded in CLI is newer than the analyzer embedded in checks. The checks bundle's older inner-label solver is NOT the oracle used here for the two label failures. The direct 0.0.83 class source is taken from the existing sibling analyzer checkout; its inner-label files are unchanged. The independent bootstrap patch is not used by this class and was not modified.

## All warning components, identities, emitted types and remaining categories

All rows emit `source_component.ftype = simple_chip`. Imported JSX also uses `<chip>`. The table describes observed metadata, not electrical roles inferred from names. U = underspecified, P = no requires_power, G = no requires_ground.

| Component | Manufacturer part / JLCPCB ID | Actual attributes relevant here | Remaining |
|---|---|---|---|
| J_PD | TYPE-C-31-M-12 / C165948 | Some signal pins is_passive; EH, GND and VBUS terminals have no attributes. Some unused signals marked NC by board | P, G |
| J_DATA | TYPE-C-31-M-12 / C165948 | Same imported omissions; different intentional NC assignments | P, G |
| U_PD | CH224Q / C46061833 | pin8 requires_power; pin11 EP has no ground requirement | G |
| D_TVS | SMF18A / C19077512 | Neither physical pin has attributes | U, P, G |
| U_ESD | USBLC6-2SC6 / C2687116 | pin2 must_be_connected + requires_ground; pin5 is_passive + must_be_connected + decoupling; others passive | P |
| Y_MCU | ABM8-272-T3 / C20625731 | All four pins explicitly is_passive | none |
| J_MOTOR | B4B-PH-K-S(LF)(SN) / C131334 | All four pins explicitly is_passive | none |
| D_STATUS | LTST-C19HE1WT / C458749 | All four pins lack attributes | U, P, G |
| Q_STATUS_R | DMN2300UFB4-7B / C154728 | All three pins lack attributes | U, P, G |
| Q_STATUS_G | DMN2300UFB4-7B / C154728 | All three pins lack attributes | U, P, G |
| Q_STATUS_B | DMN2300UFB4-7B / C154728 | All three pins lack attributes | U, P, G |
| Q_BUZZER | DMN2300UFB4-7B / C154728 | All three pins lack attributes | U, P, G |
| BZ1 | MLT-5020 / C94598 | pin3 do_not_connect; other two pins lack attributes | P, G |

`pin-inventory.json` contains all original source_component/source_port records and the exact remaining warning types. Numeric pin identities and supplier mappings are from emitted JSON and preserved import definitions, not component-name heuristics.

## What is genuinely absent versus an inappropriate chip assumption

- The six remaining U warnings correctly report missing attributes in the represented JSON. They do not prove that the corresponding physical devices require VCC or GND.
- U_PD is a documented ground-metadata omission. The retained CH224Q datasheet text's pin table calls the exposed bottom pad the common ground; the imported physical pad11/EP is already connected to GND in the emitted design but has no requiresGround. Physical connection is not the missing item. Preserve the importer physical numbering; do not rename its pad11 to datasheet pad0.
- The retained DMN2300UFB4 datasheet explicitly describes a three-terminal N-channel MOSFET and its equivalent circuit. Treating each such imported chip as necessarily having dedicated power/ground pins is inappropriate as a device-model assumption. However there is currently no typed transistor ftype or pin metadata on these emitted instances to safely exempt them with this checker. No name-based suppression or guessed all-passive annotation is proposed.
- USB connectors have mixed passive/untyped metadata, so the existing all-passive rule legitimately cannot establish an exemption. Missing metadata needs correction or a supported connector-specific model. Do not add requiresPower merely because a terminal is called VBUS: a connector's delivery direction depends on the supported part/model and use.
- SMF18A, RGB and passive buzzer likewise need supported discrete/passive models or documented pin attributes, rather than blanket mandatory chip supply assumptions. Their remaining P/G warnings stay visible pending that work. BZ1 is explicitly identified as a passive buzzer in component-plan.json; its NC pin alone prevents an all-pins-unspecified warning but does not supply semantics for the functional pins.
- USBLC6-2SC6 already has ground and VBUS-specific connection/decoupling metadata. No-power is specifically absence of `requires_power`, not missing VBUS connectivity. Whether its protection rail is to be modeled as required power needs the authoritative device schema/datasheet review, not a name-based checker patch.
- Y_MCU's passive metadata does not prove its case pads may float. Removing the blanket component-ground warning leaves any real `must_be_connected`/`requires_ground` checks intact, but supplier metadata may still need ground obligations. This candidate is not a complete ERC qualification.

## Supported importer correction path and provenance caveat

Current CLI 0.1.2446 `lib/import/import-component-from-jlcpcb.ts` fetches raw EasyEDA source, looks up manufacturer-matched `/datasheets/get?chip_name=...`, takes `pin_attributes` and `internally_connected_pins`, and runs the bundled EasyEDA conversion/TSX generator. `fetch-datasheet-pin-attributes.ts` tolerates missing data and timeout (5 seconds), continuing without enrichment. The converter resolves physical pin numbers/aliases before emitting attributes. Its generator merges inferred supply/ground/NC attributes with resolved metadata (metadata wins per pin). This is a trace of existing implementation, not approval to infer semantics ourselves from names.

Most retained imports were produced with CLI 0.1.2401 / tscircuit 0.0.3005 according to their import manifest, not the present toolchain. CH224Q and DMN2300UFB4-7B explicitly record fresh CLI 0.1.2446 imports. Preserved old import logs show success and no metadata timeout lines for the affected older parts. Therefore no claim is made that timeout caused the omissions or that current backend data still has exactly the same omissions.

Supported correction is upstream manufacturer/physical-pin metadata (or converter component typing) followed by a fresh supported `tsci import --jlcpcb --download --use-exact-footprint C...` in an isolated qualification area. Capture raw input, datasheet response and resulting metadata, compare physical pad aliases/geometry/models against the supplier, then rerun full import/source/ERC/geometry gates before adopting. Do not handpatch imports or add bogus requiresPower/requiresGround merely to silence warnings. No upstream write, publication, import replacement or external issue was attempted here.

## Label sizing root cause and scope

Core's legacy max-label calculation uses `label.length * 0.1`; with `['ALERT']`, length is 1. A subsequent opposing-side estimate does use displayed text but only reserves two 0.1 edge paddings; its character estimates do not incorporate analyzer's 0.1 interbank gap and renderer glyph widths. Hence 1.2 is accepted by core while analyzer requests 1.289/1.272. Reusing `getEstimatedPinLabelWidth(label)` in the legacy max-label calculation restores the already-existing string-label behavior and gives 1.6, which passes the unchanged analyzer.

This is intentionally a narrow representation-equivalence fix, not a claim that all rotated/top/bottom labels, arbitrary fonts, special display text or unusually wide glyphs are fully solved. Broader sizing consistency remains future work. The original core function also has other label-length estimates; they were not broadly rewritten without separate regression evidence.

## Artifacts and reproduction

- `checks-0.0.270-pin-semantics.patch`: two upstream TypeScript source changes, source-map extracted originals and candidate copies included.
- `core-0.0.2304-array-label-width.dist.patch`: one-line patch against exact published dist/index.js. Source owner is `lib/utils/schematic/getAllDimensionsForSchematicBox.ts`; replace the legacy callback `label.length * ESTIMATED_PIN_LABEL_CHARACTER_WIDTH` with `getEstimatedPinLabelWidth(label)`. This is an executable published-artifact patch, not a claimed upstream Git commit. `core-sizing-published-source.js` preserves the complete published function for review.
- `provenance.json`: bundle/fixture SHA256, exact package-lock entries, import manifest records.
- `regression.test.mjs`, `core-regression.test.mjs`: assertions; run `node --test <file>`. Set `TARGET_MODE=original` to demonstrate failures against pristine package copies.
- `core-size-probe.mjs`: live minimal Circuit renders; run `node core-size-probe.mjs`.
- `analyzer-probe.ts`: read-only direct 0.0.83 class analysis; run `./node_modules/.bin/bun analyzer-probe.ts`. Uses sibling analyzer checkout, not a newly installed package.
- `*-results.txt`, original/candidate-result.json, analyzer-results.json and size-*.json: exact runs and evidence.

Dependencies resolve read-only through symlinks to the already installed board toolchain. Full upstream repository suites, CI, complete visual QA, routed PCB qualification and manufacturing checks have NOT been run. A subsequent full isolated native rebuild is recorded in full-board-replay/REPORT.md: it preserves PCB/connectivity and removes both label findings, but adds a path-spread finding; the integration candidate is not clean. All original board warnings and gates remain unchanged. Candidates are not installed or waived.
