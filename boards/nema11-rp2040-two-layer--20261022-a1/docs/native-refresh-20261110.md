# Native WIP refresh, 2026-11-10

Source baseline: Git commit `22311adc26c8f7cfb481476320b7bee5ec646216`.
No circuit source, placement, supplier footprint/model or dependency changed.
This checkpoint refreshes native output, diagnostics and review exports only.

- Source SHA-256: `e534b89873edec43ccdd36525f7566f7a63e1ff36d9e1778b2a6ebedb37199ce`.
- Circuit JSON SHA-256: `37e2f0f8123048bf3c87dbaed27447afeeebb32125d14c78fac18f444e827903`.
- Native file: `dist/index/circuit.json`, 2,008,795 bytes.
- Toolchain: tscircuit 0.0.3121, CLI 0.1.2446, Core 0.0.2304,
  Bun 1.4.4, Node 24.22.1, locked dependencies and no production patches.
- Full input receipt: `checks/native-build-status.json`; input fingerprints
  are equal before and after build. JSON is native and has not been edited.

## Results

The native build exits 1. J_PD and J_DATA each extend their courtyard 0.25 mm
outside the board. There are no nested native errors. The placement analyzer
also reports three courtyard collisions in the optional encoder cluster and
nine orientation suggestions; retain these as separate review findings.

The netlist and source checks report zero errors/warnings. Pin semantics has
30 warnings and fails its strict gate. The schematic has four findings:
U_TEMP and D_STATUS imported label collisions, a grouping suggestion spanning
C_TEMP and the optional encoder capacitors, and the C_BOOTSTRAP orientation
diagnostic. Do not move decoupling away from its device or reorient a
bootstrap capacitor solely to silence a diagnostic; review its meaning first.
No finding has been accepted, suppressed or patched out.

34 prebuild tests, 10 emitted contracts, 657 source/import assertions and the
independent conservative geometry audit pass. These are limited checks.
The native board remains 28 by 28 mm, two copper layers, 99 source/PCB
components, 89 fitted CAD components (16 top, 73 bottom), 67 nets and 346 ports.
PCB traces and vias are both zero. Full NEMA14 feature parity, all-top upright
USB placement, rear bolt engagement, 3D assembly, routing and fabrication
remain unqualified.

Seven native A4 schematic pages cover all 99 components and 346 ports.
Top/bottom exports retain the two red boundary diagnostics. Silkscreen is
crowded, overlapping and in places off-board. The PDF and views are review
artifacts, not presentation or fabrication approval. Files remain under the
reconstruction workflow's `artifacts/20261108-reconstruction/` directory;
the PDF footer, manifests and hashes identify this fresh run.

## Reproduce and publish

After installing the locked dependencies without lifecycle scripts, run
`npm rebuild bun --offline` to activate the already installed locked runtime.
Run native netlist, placement and the fail-closed `npm run verify` workflow.
Native commands can make standard external service requests and require
appropriate authorization. Expect the failures above until resolved.

The existing tscircuit target is
`AnasSarkiz/NEMA11_RP2040_Compact_Prototype@0.6.7-reference-refactor-wip`.
Use the standard `tsci push --include-dist` publication path and independently
compare the uploaded source and `dist/index/circuit.json` bytes. An upload or
registry preview status cannot turn the failed milestone into a hardware pass.
