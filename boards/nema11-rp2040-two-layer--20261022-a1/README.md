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

**Native verification remains paused.** No current native circuit JSON/build receipt exists, and no new schematic/PCB render or hardware pass is claimed. Build traffic requires external-service approval before resuming. The older six-layer board has been removed from the working tree and defaults; it remains recoverable in Git history. Only this existing two-layer board is active.

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

Imported definitions/models must remain byte-identical to the manifest. The offline command does not call native tools or send board data. After external-validation approval, `npm run verify` performs the separate native gates. The
fresh-build receipt rejects changed inputs and stale native circuit JSON.
A nonzero native build with emitted JSON permits diagnostic analysis but is
still a failed gate. See [VALIDATION.md](VALIDATION.md) for current results.

Project links (the registry does not yet show this source refactor):

- https://github.com/AnasSarkiz/NEMA11_RP2040
- https://tscircuit.com/AnasSarkiz/NEMA11_RP2040_Compact_Prototype

Registry publication and hardware ordering remain separate approval-gated actions. There is no new V2 project.

Historical tested checkpoint `7da9556`: formatting/typecheck, 23 prebuild tests, 9 emitted
contracts, 657 source/import assertions and the conservative geometry audit
pass. PCB findings fell from 143 to 2, both USB courtyard boundary flags, with
no nested errors. Schematic still has 3 findings and pin semantics has 30
warnings. These gates remain failed. The tiny provisional bolt-head margin,
crowded labels, electrical loop placement and full mechanical fit remain open.
See the complete validation record and native top/bottom review images in
`artifacts/20261108-reconstruction/pcb/`.
Those images and the A4 PDF still show that historical checkpoint. Current offline source tests and TypeScript are recorded in the source-refactor report; native-dependent current checks remain pending. No tool candidate has been installed in production.
