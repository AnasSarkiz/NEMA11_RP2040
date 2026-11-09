# Exact integrated native electrical comparison

Candidate SHA256 verified: f590d22ad18feff381969d4dfc4032eb65f51c80465a360de8063ea7953ab538.
Baseline SHA256: b93b921adc556e840dee2bc4acb0d4f2de8fe990ebf6b6a2638e4636379acf51.

Recommendation: **Integrate this candidate as unrouted WIP only.** Its three intended electrical-placement improvements are present in actual emitted pad geometry, with no regressions in the measured loop/sense/USB/clock/flash pairs. This is not electrical fit, routing, manufacturing, or mechanical acceptance.

A prior report called the original dataset 44 pairs; it actually contains **45**, all compared here. Three supply-pad pairs improve;42 are unchanged at 0.0001 mm precision;none worsen:
- MCU33→C_IO33.1: 2.9825→0.5550 mm.
- Driver8→C_VREG.1: 2.7765→0.6000 mm.
- Driver15→C_DRV_LOGIC.1: 4.0950→2.0900 mm.

Two additional relevant ground-return bounds also improve:
- C_VREG.2→driver exposed pad29: 2.373286→1.950131 mm.
- C_DRV_LOGIC.2→driver GND18: 4.610416→3.591120 mm.

These are conservative planar native-copper AABB separations, not routed trace lengths or loop-inductance estimates. The unchanged metrics include buck input/output/bootstrap paths, driver VM/charge-pump/sense and reference pairs, oscillator links, both MCU USB series resistors, sampled connector/ESD legs and ESD capacitor links, and flash clock. Existing serious locality issues remain unchanged: buck CIN 4.9409 mm per leg, VM 6.9901/4.1577 mm, XIN 4.3989 mm, USB DP series 4.1588 mm, flash clock 14.0033 mm.

RP2040 decoupling nuance: the manufacturer's hardware guide explicitly permits pins48/49 to share a capacitor as a documented two-layer layout compromise. Per-name capacitor distances are review indicators, not standalone mandatory failure criteria. The actual shared supply/ground topology and rail behavior must be evaluated.

This review does not independently repeat the complete native diagnostic and geometric-clearance audits from the native validation study. The reported remaining two USB boundary flags and approximately 0.075 mm bolt-envelope margin remain unresolved and cannot establish hardware tolerance qualification. Routing stays disabled and exact motor gap/thread/grip data remains outstanding.

Reproduce: `python compare_integrated.py`. Full machine-readable comparison: `integrated_comparison.json` (45 pairs plus two extra ground-return pairs). No main board or import edits were made.
