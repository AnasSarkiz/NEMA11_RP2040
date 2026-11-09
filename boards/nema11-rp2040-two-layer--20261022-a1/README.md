# NEMA11 RP2040 reconstructed WIP

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

**Current main verification is paused.** A new electrical-locality placement
is integrated in source, but its main native rebuild did not finish and no
fresh circuit JSON or build receipt exists. External validation traffic needs
approval before that run resumes. The isolated candidate has native evidence
under `references/electrical-placement-20261109/`; it is not a substitute for
the main build. The last fully verified main checkpoint is Git `7da9556`.
See [the new engineering review](../../docs/engineering-review-20261109/README.md).

## Reproduce

Use Node/npm and Python 3. Dependencies are pinned in `package.json` and the
new `package-lock.json`. The archived public baseline's Bun lockfile is under
`references/public-0.6.2-review/` and is not the current lockfile.

```sh
npm ci
export PATH="$PWD/node_modules/.bin:$PATH"
export XDG_CONFIG_HOME="$PWD/.cache/config"
export XDG_CACHE_HOME="$PWD/.cache/xdg"
python3 scripts/generate_source.py
npm run format
python3 scripts/run_milestone_checks.py
```

Imported definitions/models must remain byte-identical to the manifest. The
fresh-build receipt rejects changed inputs and stale native circuit JSON.
A nonzero native build with emitted JSON permits diagnostic analysis but is
still a failed gate. See [VALIDATION.md](VALIDATION.md) for current results.

Existing public review links, which do not yet show this reconstruction:

- https://github.com/AnasSarkiz/NEMA11_RP2040
- https://tscircuit.com/AnasSarkiz/NEMA11_RP2040_Compact_Prototype

Publication remains pending explicit approval. There is no new V2 project.

Historical tested checkpoint `7da9556`: formatting/typecheck, 23 prebuild tests, 9 emitted
contracts, 657 source/import assertions and the conservative geometry audit
pass. PCB findings fell from 143 to 2, both USB courtyard boundary flags, with
no nested errors. Schematic still has 3 findings and pin semantics has 30
warnings. These gates remain failed. The tiny provisional bolt-head margin,
crowded labels, electrical loop placement and full mechanical fit remain open.
See the complete validation record and native top/bottom review images in
`artifacts/20261108-reconstruction/pcb/`.
Those images and the A4 PDF still show that historical checkpoint. Current
local code passes 25 prebuild tests and TypeScript; native-dependent current
checks remain pending. No tool candidate has been installed in production.
