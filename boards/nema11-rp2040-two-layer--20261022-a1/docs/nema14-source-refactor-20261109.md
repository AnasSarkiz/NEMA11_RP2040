# NEMA14-aligned source refactor

Revision: `0.6.7-reference-refactor-wip`, 9 November 2026.

This is the existing two-layer NEMA11 project, not a new V2 board. The obsolete
six-layer design is removed from the working tree and project defaults, with
its complete pre-removal version recoverable in Git history. See the repository
[removal record](../../../docs/legacy-six-layer-removal.md).

## Reference and actual changes

NEMA14 V2 main was verified at immutable commit
[`d9fcd4208bf7a93743447e1a0ab2c780aa08e304`](https://github.com/AnasSarkiz/NEMA14_RP2040_V2/commit/d9fcd4208bf7a93743447e1a0ab2c780aa08e304).
Its current checklist, design explanation and firmware interface are preserved
with SHA-256 provenance in `references/nema14-v2-20261109/`. No reference
repository was changed and no NEMA14 pass is counted as NEMA11 acceptance.

- Moved temperature/optional-encoder I2C to **I2C0 GPIO4/5**, RP2040 physical
  pins **6/7**, following the NEMA14 V2 pin allocation. GPIO26/27, physical pins
  38/39, are explicitly NC and reserved for later independent current telemetry.
- Reorganized the full source into **seven A4 functional sheets**: power/PD,
  programming/USB, controller/clocks, driver, temperature/optional encoder,
  RGB/power indicators, buzzer. Each of 99 source components appears exactly
  once. Export scripts and emitted-record tests now require seven pages.
- Preserved the 28 × 28 × 1.6 mm two-layer PCB, 11HS12-0674S motor at
  0.67 A/phase, four 23 mm bolt axes, complete buzzer and all existing parts.
  All 99 PCB poses and all imported definitions, footprints, symbols and
  supplier models are unchanged. Component placement is not newly qualified.
- Added a machine-readable alignment contract and offline positive/negative
  tests for the pin allocation, complete population/sheet coverage, mandatory
  buzzer, two-layer envelope, disabled routing, and honest missing-feature state.
  Supplier files and pinned reference bytes are checked by digest.
- Added exact source regeneration checking that does not modify source or
  invoke native tscircuit. Root commands/preview now select only this board.
  CI runs offline source checks only; its green status cannot mean native DRC,
  routing, mechanics or hardware passed.

## Features that still prevent NEMA14 parity

1. **Independent winding-current sensing is missing.** Moving I2C frees ADC0/1
   but does not add sensors. The reference uses two 50 mΩ inline shunts,
   INA240A1PWR/C93965 amplifiers and 100 Ω/10 nF output filters. Existing
   R_SA/R_SB are A4988 regulation shunts, not independent telemetry. At the
   NEMA11 motor's 0.67 A rating, the reference topology would nominally produce
   0.98–2.32 V around 1.65 V zero and dissipate 22.445 mW per shunt. These are
   ideal screening calculations, not a qualified design, error bound or safe
   switching-transient range. Untouched supported imports, compact placement,
   Kelvin routing, thermal/analogue review and firmware/bench checks are needed.
2. **The motor terminal remains JST.** NEMA14's WAGO 250-204/C2765063 is rated
   for bare stranded 24–16 AWG; the NEMA11 motor leads are AWG26. Directly copying
   that clamp would not qualify the leads. A compatible terminal or approved
   termination, retention and button/wire access must be established.
3. **Upright USB and all-top fitted assembly are unproven.** The preserved
   candidate still uses two flat C165948 connectors and bottom fitted parts.
   The prior GCT USB4145 locator discrepancy is unresolved. No supplier assets
   were patched and no component was dropped to claim fit.
4. **Encoder capacitors remain bottom/DNP.** NEMA14 calls for both capacitors
   fitted on top while the optional AS5600 remains bottom/DNP. That change needs
   actual placement and fresh geometry checks, rather than a metadata-only pass.
5. **Artwork, assembly and release remain open.** Exact official wordmark and
   evaluation lines, underside labels, motor/fastener/gap/insulation/USB access,
   current/thermal/USB stackup, source warnings, schematic clarity, full routing,
   CAM, stock/assembly process, firmware and physical prototype tests are not
   closed by this source refactor.

The full [requirements register](nema14-requirements-adaptation.md) retains all
NEMA14 review, original, V2, appended and acceptance requirements. The explicit
exceptions are the NEMA11 motor/28 mm/two-layer envelope and existing project
identity; unresolved features are not treated as accepted substitutions.

## Verification and stop boundary

Run from the repository root:

```sh
npm ci --prefix boards/nema11-rp2040-two-layer--20261022-a1 --ignore-scripts --legacy-peer-deps
npm run verify:offline
```

The board's `check:contracts`, `test:prebuild`, `source:check`, `typecheck` and
`format:check` are offline. `check:reference-complete` deliberately fails while
feature parity is incomplete. Results and exact input hashes are in
`checks/20261109-reference-refactor/`.

Native board build and source-uploading validation were **not attempted** in
this refactor because external-validation approval remains pending. No fresh
native receipt/JSON, seven-page render, physical connectivity, PCB DRC, CAM or
3D evidence exists for these changed nets/sheets. Updated emitted tests are
prepared but cannot pass until a fresh native build is available. Earlier
PCB images and six-page PDFs are historical. Routing remains disabled.

Registry publication was not attempted. This is not a manufacturing release,
an order instruction, a ready-to-merge claim or working firmware.

## Firmware consequence

Future NEMA11 firmware must use I2C0 on GPIO4/5 for TMP102 and the optional
AS5600. Do not read GPIO26/27 as current channels until the actual telemetry
circuit exists. Keep the driver disabled on reset; PD-good/supply interlocks,
USB recovery and the motor's correct ratings still require implementation and
bench validation. No application firmware is provided by this refactor.
