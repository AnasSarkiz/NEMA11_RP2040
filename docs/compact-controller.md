# Motor-face compact redesign

The user requires the PCB and installed USB/JST/component bodies to fit within
the motor's **28.3 × 28.3 mm maximum frame**. The OEM drawing A0071 revision 2
states that maximum; it does not state a 28.0 mm nominal frame. The initial PCB
target is 28.0 × 28.0 mm, subject to finished-outline tolerance acceptance.
The preceding routed 35 × 40 mm controller does **not** meet this new envelope.
Its zero-error DRC/connectivity results remain a useful electrical baseline.

All 82 fitted baseline components are on top. Seven bare test points are also
on top; the three optional encoder footprints remain DNP. All-top placement and
an SMT-only manufacturing process are distinct requirements: the existing PH
header and USB shell stakes need through-hole soldering. Clarification of an
SMT-only process is pending while the compact placement work continues.

The conservative top-side envelopes combine genuine copper, authored courtyards
and original supplier STEP bounds. For 89 top-side components/test points they
total 808.796 mm², larger than both a 28 × 28 mm PCB (784 mm²) and the maximum
frame square (800.89 mm²), before mounting/routing space. This is a rectangular
courtyard packing constraint, not a proof that every possible physical layout is
impossible. It establishes that a simple scaling or translation of the old board
is inadequate. Supplier footprints/models must not be scaled.

Two genuine native JLC imports are retained as candidates, not approved blanket
substitutions:

- C94598, HUAWHA/Huaneng MLT-5020 magnetic buzzer. The manufacturer specification
  dated 2021-05-27 gives 3 V rated, 2–4 V operation, 4 kHz ±200 Hz at 50% duty,
  maximum 100 mA at the rated test condition, 12 ±3 Ω coil resistance and minimum
  75 dB at 0.1 m. It has three solder terminals, including one dummy NC. The
  dimensional table says 5.2 ×5.2 ×2 mm; its drawing says 5.0 ±0.3 mm square and
  2.0 ±0.2 mm height. The conservative layout must cover this discrepancy and
  actual model bounds. It preserves an audible indicator but does not promise
  the original buzzer's sound level. Drive/current/thermal and reflow profile
  require review before selecting it. Its 6.8 ×5.76 mm authored courtyard could
  save approximately 63 mm² versus the existing buzzer.
- C160354, JST B4B-PH-SM4-TB(LF)(SN), a genuine top-entry SMT PH header with six
  pads including two hold-downs. It uses more area than the through-hole version;
  manufacturer land pattern, crimp/housing compatibility and supplier process
  acceptance still require validation. Its import alone does not solve fit.

The 3.3 V nominal rail lies inside the MLT-5020 operating range, including the
existing ±5% screen. The existing AO3400A switch and B5819W flyback path remain
part of the candidate circuit. Worst-case DC coil current at 3.465 V and 9 Ω is
385 mA; that is not its rated 4 kHz operating-current guarantee. Recalculate the
logic budget and require the documented waveform instead of assuming a DC tone.

General JLC text search currently returns unrelated matches, even for exact
known part names. Candidate identity comes from structured connector records,
exact LCSC product pages, original manufacturer documents and actual native
imports. Search-result stock must not be treated as qualified availability.
No stock is reserved.

`config/compact-controller-requirements.json` records the target.
`artifacts/requirements/compact-supplier-candidates.json` hashes the untouched
imports. Native compact source, supplier-model envelope checks, mechanical
attachment, routing and manufacturing checks must pass before replacing the
validated electrical baseline or claiming compact fabrication readiness.
