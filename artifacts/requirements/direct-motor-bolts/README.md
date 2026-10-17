# Direct motor-bolt mounting inspection

Current requirement: use four existing motor case-bolt axes, with no custom
carrier, case clamp or enclosure. The original OEM STEP shows a nominal 23 mm
square pattern and 4 mm head surfaces. Rear bolt thread, length, tolerance,
engagement and torque remain unspecified; do not infer them from front M2.5
threads or from head diameter.

`nominal-step-bolt-audit.json` records the four measured rear heads and compares
them to the historical electrical PCB. Its 25 mm holes are 1.414 mm away from
each corresponding motor axis: **the PCB alignment check fails**. The retained
zero-error copper results do not qualify a direct-mount PCB.

`motor-bolt-study.circuit.json` and `OEM-motor-native.glb` are actual native
tscircuit CLI outputs, containing the unchanged genuine motor only. Native GLB
bounds match original STEP within 0.05 mm; the measured deviation is recorded in
`native-motor-study-verification.json`. Original lead stubs and front shaft are
preserved. There is no PCB/carrier or invented replacement hardware in this study.

The default assembly builder rejects the superseded carrier. Reproducing frozen
carrier records requires `--historical-carrier` and does not approve that design.

See [current mounting requirements](../../../docs/direct-motor-bolts.md).
**NOT FOR FABRICATION.**
