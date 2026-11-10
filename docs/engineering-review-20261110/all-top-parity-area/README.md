# NEMA11 all-top parity courtyard screen

Source-only engineering study dated 2026-11-10. Fixed user target remains 28 × 28 mm, 23 mm bolt pitch, two copper layers. No active-board changes, native build, publication or manufacturing approval.

## Result
Two hypothetical C5815189 upright connectors leave an archived baseline of 679.353717 mm² fitted courtyard area. Exact pinned NEMA14 telemetry adds 79.966319 mm², yielding 759.320036 mm² against provisional available area 714.602218 mm²: excess 44.717818 mm². Fitting the two encoder capacitors adds 3.827695 mm²: total 763.147731 mm², excess 48.545513 mm².

Telemetry adds ten fitted components: two each INA240A1PWR/C93965, ERJL06KF50MV/C713441 0.05 Ω, A_0402WGF1000TCE/C25076 100 Ω, CL05B103KB5NNNC/C15195 10 nF, CL05B104KO5NNNC/C1525 100 nF bypass. Source topology and catalog are saved. Existing A4988 regulation shunts are retained, not replaced or counted twice.

NEMA14 fits C_ENCODER/C1525 and C_ENCODER_BULK/C52923; recovered NEMA11 marks both DNP. They add two fitted parts for parity (89→99→101). U_ENCODER stays DNP and its optional reservation is excluded. Existing driver decoupling is already in baseline; any newly required second local VBB bypass is not included.

## Reproduce
Run python calculate.py and python -B -m unittest -v test_calculate.py in this directory.
Snapshots are fetched UTF-8 source content; every saved source is verified against its pinned Git blob SHA before calculation. provenance.json contains exact source URLs and hashes. The archived NEMA11 area report is also SHA-256 checked, so a changed baseline cannot silently reuse these totals. Polygon areas use shoelace, independent of orientation; non-finite coordinates are rejected. Tests cover correct and reversed polygons, invalid/missing geometry, non-finite coordinates, modified-source and changed-baseline rejection, and expected totals. No tools or dependencies are installed.

## Limits
This fails a simplified screen requiring wholly contained, nonoverlapping courtyards outside four provisional R2.35 bolt-head disks. It is not proof that physical bodies cannot fit. Raw board area is 784 mm². Packing, copper routing/vias, edge setbacks, power widths, thermal performance, maximum body tolerances, cable envelopes, screw/tool access and qualified assembly process remain unproven. Courtyard area is not model/body area.

Both examined upright connector footprints remain unqualified: C5815189 locator width 1.509979 mm versus 1.01±0.05 mm; C5291559 width 1.09982 mm versus maximum 1.06 mm, with longer stakes. See archived upright-usb-report.md. The baseline uses the former hypothetically, not an approved substitution.

No alternative is silently authorized. Preserve the fixed 28 mm / two-layer target and current two-face fallback while qualifying supported geometry and assessing a redesigned part set. A larger board or changed assembly requirement would require a user decision. Even passing this screen would not prove placement or routing feasibility.

## Evidence
Pinned NEMA14 commit d9fcd4208bf7a93743447e1a0ab2c780aa08e304. NEMA11 baseline: ../../engineering-review-20261109/upright-usb-report.md. NEMA11 DNP status: ../../../boards/nema11-rp2040-two-layer--20261022-a1/index.circuit.tsx. The archived rounded baseline is reused, not represented as fresh native output.
