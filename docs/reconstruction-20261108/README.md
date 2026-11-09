# NEMA11 reconstruction checkpoint

This is a new reconstruction of the existing NEMA11 project, not a recovered
byte-identical copy and not a new V2 board. It starts from freshly cloned public
GitHub main `1233ccdf803a1221820f28eabf4791b4a7cfe90e` (version 0.6.2).
The unpublished local checkout and its later commits could not be recovered
after an execution-workspace reset. Exact placement and generated outputs from
those commits are not available. Historical test results do not validate this
reconstruction. The existing board path and package identity are retained.

The completed main-project result at `7da9556` is in [FINAL-CHECKPOINT.md](FINAL-CHECKPOINT.md).
For subsequent work and the current incomplete native verification, see
[the engineering review](../engineering-review-20261109/README.md).
The recipe and historical constraints below are retained for provenance.

## Scope and gates

- Existing `boards/nema11-rp2040-two-layer--20261022-a1` project.
- Existing `AnasSarkiz/NEMA11_RP2040_Compact_Prototype` package identity.
- 28 × 28 × 1.6 mm PCB, two copper layers, 0.67 A motor, required buzzer.
- Four existing motor-case bolt axes at X/Y = ±11.5 mm; provisional Ø2.7 mm
  holes and R2.35 mm head envelopes. No custom carrier.
- No handmade or patched component, symbol, pin map, footprint or CAD asset.
- Routing stays disabled. No fabrication, fit, assembly or physical-test claim.
- Publication remains pending explicit approval. No push, merge or registry
  upload is authorized by this reconstruction record. Historical repository
  publication instructions do not override the latest task restriction.
- Complete-history Git bundles are to be saved privately after checkpoints.

## Lost local commit identities

These identities are retained only as historical references; their objects
were not recovered and this repository does not claim to contain them:

- `125478b513a4b07df0d4f81a79a6106c1be22592`: startup and USB protection.
- `218655350e92a6e482ff284d6f176a73dfe8cc7f`: two-edge placement and schematic.
- `a4c86d44a55069169e92baafe76d7cc572f8a495`: all-top feasibility study.
- `7bb913a7162b82c5e8c60147bd4182d6925ff2a8`: compact PD/FET candidate.
- `1180e9a5985f7394e48348325024d377f248a31b`: assembly review.

The earlier complete layout, native output, exact lockfile, upstream bug patches
and placement optimizers were not recovered. They must be regenerated or
reimplemented and tested. Their historical passing results must not be reused.

## Reconstructable electrical changes

Retained engineering records specify these candidate changes. Newly imported
bytes and emitted native connectivity must be checked before relying on them:

1. R_ENABLE and R_SLEEP: C25744, 10 kΩ each. Add C_ESD: C1525, 100 nF,
   DATA_VBUS to GND, adjacent to U_ESD.
2. U_PD: CH224Q C46061833. Retain physical pins 1=PD_VHV, 6=PD_CC2,
   7=PD_CC1, 8=PD_VBUS, 9=PD_CFG, 10=PD_GOOD, 11=GND. Explicit NC 2–5.
   Retain 56 kΩ R_PD_CFG and 0 Ω R_PD. Fresh supported import required.
3. Q_BUZZER and Q_STATUS_R/G/B: DMN2300UFB4-7B C154728. Physical pin 1
   gate, pin 2 drain, pin 3 source. Fresh supported import required.
4. Buzzer gate resistor: C11702, 1 kΩ from BUZZER_PWM to BUZZER_GATE.
   Gate pulldown: C25744, 10 kΩ BUZZER_GATE to GND. Drain BUZZER_SINK,
   source GND. Keep BZ1 C94598, flyback diode and 10 µF bypass unchanged.
5. For each status color C: add 1 kΩ C11702 from LED_C to STATUS_C_GATE,
   and 10 kΩ C25744 from STATUS_C_GATE to GND. FET drain STATUS_C_C,
   source GND. Retain existing 1 kΩ LED series resistors and DATA_VBUS anode.
6. MCU GPIO assignments and all other controller features remain unchanged.

No telemetry amplifier, alternate motor driver, smaller bulk capacitor,
upright USB connector or motor connector substitution is approved by this
recipe. Those feasibility alternatives had unresolved qualification or fit.

## Recovered PCB anchors, not a complete placement

| Ref | X mm | Y mm | Rotation | Side |
| --- | ---: | ---: | ---: | --- |
| J_PD | 0 | 8.65 | 180 | top |
| J_DATA | 8.65 | 0 | 90 | top |
| J_MOTOR | 3.9 | -11.1 | 180 | top |
| C_BULK | -4.9 | -9 | 90 | top |
| U_DRV | 2 | -3.2 | 270 | top |
| U_ESD | 9.8 | 0 | 0 | bottom |
| C_ESD | 7.35 | 0 | 270 | bottom |
| U_PD | -1.4 | 7.6 | 270 | bottom |
| Q_STATUS_R | 7.2567 | 7.1577 | 90 | bottom |
| Q_STATUS_G | 7.3914 | -12.5292 | 180 | bottom |
| Q_STATUS_B | 3.5599 | -12.5616 | 180 | bottom |
| Q_BUZZER | -10.7027 | 3.9654 | 270 | bottom |
| R_BUZZER_GATE | -6.1146 | 4.0305 | 0 | bottom |
| R_BUZZER_PD | -3.906 | 3.8227 | 180 | bottom |
| R_STATUS_R_GATE | -6.4 | 2.4 | 90 | bottom |
| R_STATUS_R_PD | -2.4 | 10 | 90 | bottom |
| R_STATUS_G_GATE | 0.2 | 5.2 | 90 | bottom |
| R_STATUS_G_PD | -2.4 | 12.2 | 90 | bottom |
| R_STATUS_B_GATE | 6.2 | 12.2 | 90 | bottom |
| R_STATUS_B_PD | 7.4 | 12.2 | 90 | bottom |

These are unrouted candidate coordinates, not approved placement. Passive
clusters not listed above are unrecovered. Do not assume they remained in
their public-baseline positions. Gate pulldowns must be reviewed locally to
their FETs before routing. A new placement may improve upon the retained poses.

## Recovered schematic behavior

Native board layout used `schLayout={{ layoutMode: "relative" }}` because
`schAutoLayoutEnabled={false}` alone did not prevent automatic matching of
sheet children. Add supported `schRotation` handling in the generator.
Automatic trace labels and maximum schematic trace distance 4 were used.
Exact rotations for 57 symbols are not recovered and require fresh review.

Known Q_STATUS schematic positions: R (21.6375, 12.7), G (24.9375, 12.7),
B (28.2375, 12.7); gate resistors were 1.5 mm left, pulldowns 1 mm left
and 2 mm below at -90°. U_PD was (11, 15.72), Q_BUZZER (8.5, 3.8).
Positions are layout evidence only, not assurance of readability.

## Tooling and verification to reproduce

Previously used exact tool versions: tscircuit 0.0.3121, CLI 0.1.2446,
core 0.0.2304, Bun 1.4.4, TypeScript 5.9.3, Prettier 3.6.2. Fresh dependency
resolution must be recorded because the prior lockfile was lost.

Build gating must delete stale output, fingerprint all relevant inputs,
serialize concurrent runs and reject malformed or incomplete checker logs.
Native schematic-check exit 0 can still contain findings. Generated circuit
JSON must never be patched. Run format, typecheck, structural tests, native
build and all five required native source checks. Emitted-output assertions
must inspect actual supplier identities, physical pin nets, passive values,
preserved features, outline/layers, import hashes and zero traces/vias.

Expected candidate population from the recipe is 99 source components,
89 fitted parts (16 top, 73 bottom). This is an expectation to test, not a
current result. Historic 17 PCB findings and 3 schematic findings applied to
lost bytes only. All gates remain unpassed for this reconstruction.

## Exact buzzer evidence now available

The adjacent `exact-buzzer/` contains a newly retrieved original manufacturer
PDF linked by LCSC C94598, dated 2021-05-27, and a fresh review/bench plan.
It states 3.0 Vo-p rated, 2–4 Vo-p operation, 4,000 ±200 Hz, 50% square wave,
≥75 dB at 10 cm, 12 ±3 Ω coil resistance, and 250 °C maximum reflow peak.
The 100 mA quantity is not explicitly defined as peak, RMS or average.
Older 2017 ratings cannot be transferred. 3.3 V is within the stated voltage
range, but actual waveform, freewheel current, acoustics and temperature still
require measurements. Preserve the buzzer and clamp.

## Mechanical and assembly limits remain open

Existing motor-bolt shank/thread/head/grip, engagement, insulation and actual
PCB gap are unverified. Front motor M2.5 data is not rear-bolt data. Earlier
2 mm preview gap is not approved clearance. Current layout needs fresh full
3D measurements. All-top assembly with two upright USB-C is a study, not a
demonstrated fit. Imported USB4145 locator mismatch remains unresolved.

JLCPCB 2.5 mm body-to-edge and ≥5 mm rail guidance must be checked against
the actual panel/connector overhang arrangement. Generic clauses alone do
not establish failure or assembly acceptance. Mixed SMT/through-hole support
does not qualify any particular connector, cost or process.
