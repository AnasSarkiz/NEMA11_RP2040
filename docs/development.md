# Current development environment

Work on `boards/nema11-rp2040-two-layer--20261022-a1` in the existing checkout.
The root package, preview and TypeScript configuration select this board only.
Historical root `src/`, `examples/`, `tools/pcb` and retained prototype folders
are not the current board's toolchain or validation target.

## Offline source verification

From the repository root:

```sh
npm ci --prefix boards/nema11-rp2040-two-layer--20261022-a1 --ignore-scripts --legacy-peer-deps --no-audit --no-fund
npm run verify:offline
```

The lockfile controls the active dependencies. Installation may fetch packages;
`--ignore-scripts` prevents dependency lifecycle hooks. The verification itself
uses local Python/TypeScript/formatting and source-generation checks. The active `source:check` regenerates in memory and compares the result with
`index.circuit.tsx` without modifying it.

These checks do not invoke native rendering, autorouting, registry operations,
or source-uploading tscircuit commands. They do not validate native output or
approve copper, mechanics, fabrication or physical hardware.

## Native work is separate

`npm run build` and `npm run dev` select the active two-layer source, but they
are manual native entry points, not part of offline validation or CI. A native
build can contact `api.tscircuit.com`; do not run it while source-upload approval
is pending. Do not publish or upload a registry package without authorization.
After an approved build, use the active board's validation instructions and
fresh input-bound reports. Never reuse old reports as evidence for changed
source. Never print credentials or tokens.

The former root setup and native scripts are retained only where needed for
historical four-layer/MCU evidence. They are not recommended setup or validation
for current work. See [scoped six-layer deletion](legacy-six-layer-removal.md).

## Separate motor assembly preview

`npm run build:assembly` and `npm run dev:assembly` select the genuine motor
assembly around the same active PCB. The ordinary electrical build still selects
`index.circuit.tsx`. The preview is an exploded review, not an approved hardware
stack; native errors remain failures. Assembly commands are manual native work
under the same service-access permission rules above, never part of offline CI.
