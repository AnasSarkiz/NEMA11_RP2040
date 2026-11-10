# NEMA11 RP2040 NEMA14-aligned WIP

This continues the same NEMA11 board and package. The local unpublished work
was lost after a workspace reset. This revision is reconstructed from public
GitHub main `1233ccdf803a1221820f28eabf4791b4a7cfe90e` and retained engineering
evidence. It is not byte-identical to the lost 0.6.5 layout. See the repository
[reconstruction record](../../docs/reconstruction-20261108/README.md).

The candidate retains a 28 × 28 × 1.6 mm two-layer PCB, both USB-C inputs,
RP2040, A4988, buzzer, temperature sensor, RGB indicator, motor connector,
debug points and optional DNP encoder. The two flat USB connectors are placed
at adjacent board edges. Compact CH224Q and DMN2300UFB4-7B imports are being
requalified. All-top assembly with two upright USB-C remains a separate
feasibility question, not a verified fit.

**Unrouted, untested prototype. Not fabrication-ready.** Native routing remains
disabled until schematic, BOM, placement and mechanical gates pass. Do not
order or infer acceptance from a render. No historical passing check validates
this reconstructed revision.

**Current source refactor: 0.6.7-reference-refactor-wip.** The reference is pinned to NEMA14 V2 commit `d9fcd420`. I²C now uses GPIO4/5 (I2C0), leaving ADC0/1 explicitly NC for the still-missing winding-current telemetry. There are seven functional A4 sheets, with all 99 source components preserved. The PCB placement and all supplier files are unchanged. See [the source-refactor record](docs/nema14-source-refactor-20261109.md).

**Fresh native WIP checkpoint, 2026-11-10.** The current source now has native
[`dist/index/circuit.json`](dist/index/circuit.json), a full-input hash receipt,
seven A4 schematic pages and top/bottom PCB review views. Native build and
strict milestone gates fail: two USB boundary errors, 30 pin warnings and
four schematic findings remain. The placement analyzer additionally reports
three courtyard collisions and nine orientation suggestions. All findings are
retained. See [the native refresh report](docs/native-refresh-20261110.md).
The older six-layer design remains deleted and recoverable in Git history.

## Reproduce

Use Node/npm and Python 3. Dependencies are pinned in `package.json` and the
new `package-lock.json`. The archived public baseline's Bun lockfile is under
`references/public-0.6.2-review/` and is not the current lockfile.

```sh
npm ci --ignore-scripts --legacy-peer-deps
export PATH="$PWD/node_modules/.bin:$PATH"
export XDG_CONFIG_HOME="$PWD/.cache/config"
export XDG_CACHE_HOME="$PWD/.cache/xdg"
npm run source:generate
npm run verify:offline
```

Imported definitions/models must remain byte-identical to the manifest. The offline command does not call native tools or send board data. For authorized native work, `npm rebuild bun --offline` activates the locked runtime after the script-free install, then `npm run verify` performs the separate native gates. The
fresh-build receipt rejects changed inputs and stale native circuit JSON.
A nonzero native build with emitted JSON permits diagnostic analysis but is
still a failed gate. See [VALIDATION.md](VALIDATION.md) for current results.

Project links:

- https://github.com/AnasSarkiz/NEMA11_RP2040
- https://tscircuit.com/AnasSarkiz/NEMA11_RP2040_Compact_Prototype

The publication target is the existing package, version `0.6.7-reference-refactor-wip`, with the native `dist/index/circuit.json` included. Publication is not a hardware release. There is no new V2 project.

Historical checkpoint `7da9556` remains available in Git history. Current
review images and the seven-page A4 PDF under
`artifacts/20261108-reconstruction/` were refreshed on 2026-11-10; that folder
name identifies the reconstruction workflow, not the generation date.
The source and supplier imports were not changed by this native refresh.
No upstream tool candidate has been installed in production.
