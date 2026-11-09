# Portable NEMA11 electrical placement study

Read `INTEGRATED-REVIEW.md` for the exact candidate recommendation and `REPORT.md` for the detailed electrical assessment. The integrated candidate is recommended as **unrouted WIP only**, not electrical, mechanical, manufacturing or routing acceptance.

## Frozen inputs
`input-bindings.json` binds the baseline commit and hashes of every saved input. Included are only the two native circuit JSON snapshots, baseline placement/connections configuration, and the existing standalone geometry audit helper. No imports, node_modules, build toolchain, or CAD assets are needed to replay this numerical study.

- Baseline circuit SHA256: b93b921adc556e840dee2bc4acb0d4f2de8fe990ebf6b6a2638e4636379acf51.
- Integrated candidate SHA256: f590d22ad18feff381969d4dfc4032eb65f51c80465a360de8063ea7953ab538.
- Baseline commit: 7da9556d18d4e8b54cc790c58dd25d4b487f34eb.

The scripts refuse a different baseline/candidate circuit hash rather than silently replaying against changed geometry. The saved `inputs/board` is a minimal analysis input bundle, not a buildable tscircuit project. Native source regeneration requires the actual repository/toolchain and is outside this replay.

## Run
Python 3 standard library only. From this directory:

```sh
sha256sum -c SHA256SUMS
export NEMA11_OUTPUT_DIR="$(mktemp -d)"
python review.py
python candidates.py
python crystal_cluster.py
python driver_cluster.py
python driver_two_caps.py
python compare_integrated.py
for f in metrics.json nearest_rail_caps.json independent_candidates.json crystal_cluster_candidates.json driver_cluster_candidates.json driver_two_caps_candidates.json integrated_comparison.json; do
  cmp "$f" "$NEMA11_OUTPUT_DIR/$f"
done
```

Run `review.py` before `compare_integrated.py` when using a fresh output directory. The candidate scripts also regenerate the baseline metrics. Without an output override, scripts write their JSON files beside the scripts. No board files are written.

Optional environment path overrides:
- `NEMA11_BOARD_DIR`: directory containing baseline `config/placement.json`, `config/connections.json`, `scripts/audit_placement_geometry.py`, and normally `dist/index/circuit.json`.
- `NEMA11_BASELINE_JSON`: alternative path to the exact SHA-bound baseline JSON.
- `NEMA11_CANDIDATE_JSON`: alternative path to the exact SHA-bound integrated JSON.
- `NEMA11_OUTPUT_DIR`: output directory for regenerated study data.

The search algorithms and original conclusions are unchanged by this portability pass. `candidates.py` generates **independent**, not jointly legal, possibilities. `crystal_cluster.py` and `driver_cluster.py` reproduce **rejected** trials. Do not apply those trial files as a solution. `driver_two_caps.py` reproduces the useful combined VREG/logic-cap pair. The integrated comparison covers 45 original pad pairs plus 2 additional ground-return pairs; the earlier 44 count was a reporting mistake, already corrected.

## Sources and scope
- RP2040 manufacturer datasheet, retained repository `references/manufacturer/RP2040.pdf`, extracted here as `rp2040.txt`; §§2.9 and2.16. https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf
- Raspberry Pi, Hardware design with RP2040, release2/build2026-08-20; §§2.1–2.4 and2.7. https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf
- Diodes AP63200/AP63201/AP63203/AP63205, DS41326 Rev3-2 November2024, p15. https://www.diodes.com/datasheet/download/AP63200-AP63201-AP63203-AP63205.pdf
- Allegro A4988, Rev8 April2022, p12. https://www.allegromicro.com/-/media/files/datasheets/a4988-datasheet.pdf
- ST USBLC6-2, DS4260 Rev7 December2021, §2.3 p6. https://www.st.com/resource/en/datasheet/usblc6-2.pdf

Sources checked 2026-11-09. The saved geometries, not future versions of linked documents, define the numerical replay. The reports retain the manufacturer nuance permitting a deliberate shared decoupling capacitor for adjacent RP2040 pins48/49 on a two-layer design. Distances are conservative planar AABB pad separations, not routed trace lengths, loop inductance, or proof of electrical performance.

For backup, copy all regular files and `inputs/`; omit `__pycache__/` if present. `SHA256SUMS` covers all durable files except itself, caches and replay output. `PORTABILITY-VALIDATION.json` records the byte-identical artifact replay.
