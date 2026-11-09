# CLI 0.1.2446 analyzer 0.0.83: bootstrap orientation candidate

## Verified result

Against the actual CLI analyzer version, the generic fix changes the freshly built NEMA11 native JSON from **3 findings to 2**. The only removed issue is C_BOOTSTRAP `TwoPinComponentShouldBeVertical`. U_TEMP and D_STATUS `SchematicBoxInnerLabelCollision` objects are byte-for-byte equivalent as parsed objects before and after. There are no new or otherwise changed findings. Neither board files nor installed production dependencies were modified.

Input SHA256: `056b8d48bb7fb60edcb96af118652b53589711eab4c5e885eff4c0b32db8ce91`.

The exact native input is frozen at `validation/current-native-input.json`. Comparison evidence is `validation/current-native-comparison.json`; baseline/patched issues, text output and execution logs are adjacent. This is a pure local analysis replay, not a new circuit/native build and not a pass of the board's production gate. The two imported-symbol label findings remain open, as do independently reported PCB issues.

## Actual owner and version provenance

- Owner: https://github.com/tscircuit/circuit-json-schematic-placement-analysis
- Consumer: installed `@tscircuit/cli` 0.1.2446 declares analyzer `https://jscdn.tscircuit.com/@tscircuit/circuit-json-schematic-placement-analysis/0.0.83.tgz`.
- Official tag `v0.0.83`: `9a3660921ddf7d262e705cbe628ede716c0c0110`.
- Official tarball SHA256: `64b676c337f4082e6be47f7ab47a4a94636c7c43e5e0b620e1acd60784dbcc4c`.
- All **94** packaged TypeScript library source files match that tag exactly. See `validation/official-provenance.json` and retained `validation/official-0.0.83.tgz`.

This isolated worktree is based on that tag, branch `fix/bootstrap-rail-orientation-cli083`. The older checks 0.0.270 / cece282 study is preserved separately at `../nema11_schematic_tool_reconstruction`; its 1→0 current-input result reflects its older label checker and must not be substituted for the CLI's 3→2 result.

## Generic fix

SW is a switching output typed `provides_power`, not a demonstrated DC rail. A 100 nF capacitor returns to BST on the same chip. Neither node carries explicit rail metadata. The existing rail checker treats the power-output flag as sufficient for a compulsory vertical shunt layout.

A shared `PlacementNetworkIndex.isLocalFloatingChipCapacitor` helper exempts only ambiguous local chip-return capacitors. It requires distinct terminal nets, no explicit power/positive/ground net, no ground/fixed-voltage/do-not-connect evidence, one inferred supply node provided solely by the same chip, exactly one external peer on the other terminal, and unambiguous same-scope chip/capacitor placement. Additional supply loads/sources, explicit rails/voltages, different hosts or scope, and resistors are not exempted. No names, port hints, designators or part numbers establish electrical roles.

Both orientation solvers use the helper. Otherwise the generic `CapacitorSymbolHorizontal` warning is revealed after the rail warning is removed by analysis deduplication. The helper establishes insufficient evidence for mandatory rail orientation, not proof of a specific electrical role. This remains a candidate for upstream review and approved dependency integration.

## Verification

- Baseline pinned 0.0.83 source: regression fails at expected bootstrap assertion (`regression-baseline.txt`).
- Patched source: 15 variants pass under Node and Bun 1.4.4 (`regression-patched.txt`, `regression-bun.txt`).
- Snapshots stack schematic above analysis. Original and renamed topology are accepted. Explicit power/positive/ground, pin-ground, fixed voltage/zero voltage, another supply, different host/scope, requires-only source, external load and resistor negative controls retain warnings.
- Existing native decoupling and pull resistor warnings remain present. Inputs remain unmodified by analysis.
- Fresh native input exact comparison: **3→2**, only bootstrap issue removed, both label issue objects unchanged.
- Focused TypeScript check of all library sources, new test and required snapshot helper: passes (`typecheck-focused.txt`).
- `git diff --check`: passes.
- Whole upstream suite and Biome check not run. Full-suite fixtures can invoke circuit rendering; this work was restricted to pure local analysis. Previous older-version full typecheck showed missing Bun typings in the reused dependency environment; the current focused code/test typecheck passes.

No native tsci build, placement API, registry write, issue/PR creation, commit, publication or push was performed. No production imports, symbols, pins, footprints or CAD changed. Existing installed dependencies were only read through a workspace symlink.

## Deliverables and reproduction

- `validation/source-only.patch`: narrow library changes.
- `validation/upstream-candidate.patch`: source, regression fixture/test and 15 snapshots.
- `validation/upstream-cli083.bundle`: verified complete-history bundle at actual owner tag.
- `validation/official-0.0.83.tgz`: exact official package, for independent provenance.
- `validation/portable-source.tar.gz`: patched source plus tests and evidence, excluding `.git` and `node_modules` links and duplicate upstream bundle/tarball.
- `validation/dependency-reference-package-lock.json`: recorded test dependency environment, not an instruction to modify production.

Clone bundle with `git clone upstream-cli083.bundle owner`, apply `upstream-candidate.patch` from that checkout, and provision suitable dependencies separately. The portable source archive already contains patched code and the Node transpilation loader. It does not include offline npm dependencies.

    node --loader ./validation/loader.mjs --test tests/cases/local-floating-chip-capacitor.test.ts
    BASELINE=1 node --loader ./validation/loader.mjs --test tests/cases/local-floating-chip-capacitor.test.ts
    node_modules/.bin/bun test tests/cases/local-floating-chip-capacitor.test.ts
    node node_modules/typescript/bin/tsc -p validation/tsconfig.json --pretty false
    BASELINE=1 node --loader ./validation/loader.mjs validation/compare-current-native.mjs
    node --loader ./validation/loader.mjs validation/compare-current-native.mjs

BASELINE uses saved pristine 0.0.83 versions of the three edited files; everything else remains the same. Current-native replay defaults to the frozen bytes, or accepts NATIVE_JSON_PATH to inspect a later authorized export. The regression's historical native power-sheet fixture is explicitly documented in `fixture-provenance.json`; no test variant changes the board.
