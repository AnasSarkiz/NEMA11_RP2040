> Historical pre-access review. Read the [2026-10-17 source/access update](access-restored.md) for resolved download/authentication blockers and the exact v1.13.0 inventory.

# Engineering review — requirements milestone

## Reference identity

The required baseline is the published tscircuit package
`AnasSarkiz/NEMA14_RP2040@1.13.0`. It has not yet been retrieved. The accessible
GitHub `main` commit `e04df7a3b606b280389109405de96601e9430695` records v1.8.2.
The review branch `fix/nema14-ai-review-20261013` at
`596a8b8a5187dfd60924de4b8ac0c93e13d99680` records v1.12.0. Its native board
SHA-256 is `67820851170068eb092c3b611949ce67218b58f1049365fd317e8c1a513645e6`.

The v1.12.0 source uses **CH224K**, not the requested **CH224A**. Its A4988,
component inventory and pin nets are recorded only as inspection evidence.
Do not copy that PD pin map or declare feature parity until v1.13.0 is read.
The independently documented RP2040 subsystem can be developed and checked
against its manufacturer documents while exact controller-baseline access is
pending; its GPIO allocation remains subject to the v1.13.0 comparison.
No files, branches or remote refs in NEMA14 have been modified.

## Motor and attachment

The user's current-drawing requirements are 0.67 A/phase, maximum 28.3 mm
frame, maximum 33 mm body length, 23 mm front mounting pitch, and M2.5 front
threads. Original motor PDF and STEP retrieval currently receives HTTP 403
from the environment proxy. These dimensions are user requirements, not a
claim of independent document or CAD verification.

The front thread pattern must not be reinterpreted as rear threads. Neither
rear mounting holes nor a rear shaft is established. Thread depth, engagement,
shaft diameter/length, pilot diameter, lead-exit location/tolerances and winding
color pairing remain unknown. No attachment hardware is selected yet.

After obtaining the original drawing/model, evaluate a front-supported adapter
or a body clamp with a documented retention method. An adapter must preserve
front shaft/pilot access and avoid replacing motor case screws without supplier
approval. A clamp needs verified pressure, retention and thermal implications.
The PCB outline is not selected merely by scaling the NEMA14 board. Connector,
component, tool and motor-lead envelopes must fit the actual assembly.

Route bare motor leads toward the fitted JST edge with a defined bend radius,
strain relief and access to the mating housing. Do not invent a connector on
the motor. If the v1.13.0 JST is the v1.12.0 SH part, verify the BM04B-SRSS-TB
header, SHR-04V-S housing, appropriate SSH-series contacts, wire gauge/insulation
and per-contact hot current rating from JST documentation. Reference coil order
is 1:A+, 2:A−, 3:B+, 4:B−; motor lead colors must come from the NEMA11 drawing
and be checked with continuity. Do not carry over NEMA14 motor lead colors.

Optional encoder circuitry remains DNP. A front shaft does not establish an
encoder magnet position, rear shaft, air gap or usable encoder assembly.

## Conditional A4988 electrical screening

These calculations apply only if the published baseline retains A4988 and its
two 0.24 Ω shunts. Verify that premise before circuit implementation.

`Itrip = Vref / (8 × Rsense)` gives 1.2864 V for exactly 0.67 A nominal.
Setting the nominal limit precisely at the motor rating leaves no tolerance
margin. The preliminary candidate 19.6 kΩ/10 kΩ divider on 3.3 V gives
1.114865 V and 0.580659 A. Exhaustive 32-corner screening with ±5% rail,
±1% resistors and a provisional ±5% driver gain allowance yields
0.512007–0.655234 A. **This is an assumed design budget, not a guaranteed
manufacturer bound or a final BOM.** Do not increase the peak trip by √2 just
because an A4988 full-step holds approximately 70.71% in each phase; confirm
the motor current convention, microstep operation and actual measured currents.

At a conservative 0.67 A per-phase sizing load, each 0.24 Ω shunt dissipates
107.736 mW. A 125 mW part is already at 86.2% of nameplate before ambient
derating, pulse limits and motor heating. Use at least a 250 mW candidate before
checking the actual manufacturer's hot derating curve; a larger rating or lower
resistance may be necessary. Retain independent Kelvin sense paths and a quiet
common ground reference. Do not simply widen a shared return and assume offsets
are eliminated.

At equal bridge resistance, 0.67 A gives 3.65 times the conduction loss of the
v1.12.0 nominal 0.350765 A setting. A conservative simultaneous two-phase bound
is `Pbridge = 2 × 0.67² × Rbridge_hot = 0.8978 × Rbridge_hot` watts, plus
switching, control and charge-pump losses. Normal sine microstepping has a
different sum of squared phase currents; the conservative bound does not assert
that both phases normally remain at Itrip. Junction temperature cannot be
calculated honestly without hot RDS(on), board-specific thermal resistance,
ambient/motor heating and duty. Motor winding loss likewise requires the
actual phase resistance. No temperature prediction is released.

The legacy IPC-2221 isolated-track screen at 0.67 A and 30 °C rise gives
0.0888 mm for 35 µm outer copper and 0.4618 mm for 17.5 µm inner copper.
These are screening outputs, not routing recommendations. Preserve at least
the requested 0.30 mm drill / 0.45 mm via pad. Review every actual neck,
transition, supply feeder, sense path and return using its own current budget;
input current is not the sum of chopper phase currents. Thermal spreading,
barrel plating, pad escape lengths and regenerative transients require separate
checks. Finished copper/stackup and via-in-pad processing need supplier acceptance.

## Access and manufacturing blockers

- Allow `files.omc-stepperonline.com` for the original PDF/STEP.
- Allow `registry-api.tscircuit.com` for exact v1.13.0 public source and release
  identity. Other saved tscircuit domains support registry/docs/publication.
- The native CLI reports no tscircuit login; `TSCIRCUIT_TOKEN` and known local
  tscircuit configuration are absent. Supply the token securely in environment
  settings for publication to the separate NEMA11 package, never in chat or Git.
- Verify CH224A manufacturer pin map, 15 V selection, PG electrical behavior,
  default disabled motor state and ADC scaling against the published source.
- Stock, supplier footprint/MPN acceptance, pickup rotation, panel/process,
  soldering, thermal-via treatment and assembly quotation are unconfirmed.

Network additions and the token requirement were saved as an environment draft.
A saved draft does not apply runtime changes or publish the environment. Review,
save and publish through environment settings, then retry the blocked retrievals.
No physical or manufacturing checks are represented as passed.
