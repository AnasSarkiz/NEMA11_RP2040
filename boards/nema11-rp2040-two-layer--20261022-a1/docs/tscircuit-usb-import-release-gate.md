# C5815189: require a corrected released import

The user's requirement is to resolve the USB4145-03-0070-C locating-hole
omission through a new tscircuit version and its supported JLCPCB importer.
Keep original imported files unchanged. Do not add the missing hole in the
board, patch a component wrapper, or claim the alternate USB-C candidate fixes
this import. The current board's C165948 candidate remains unapproved WIP.

The baseline exact import made by CLI 0.1.2261 has one explicit Ø0.7099808 mm
NPTH. The GCT manufacturer drawing, page 2, requires two Ø0.71 mm locating
holes at 8 mm pitch. Four plated shell slots do not replace the second NPTH.
The regression screen in `checks/usb-locator-baseline.json` fails as expected.

A new version is **not yet verified to fix this**. npm metadata requests for
both CLI and tscircuit return HTTP 503 through the cloud proxy. No dependency
pin, installed library, original import or board source was modified. The
underlying cause may be supplier data or conversion; raw current supplier
input is needed to distinguish them.

When network access returns:

1. Query the published CLI and tscircuit versions and inspect relevant release
   changes; record exact versions and install without weakening integrity checks.
2. In an isolated candidate directory, run the new supported CLI:
   `tsci import --jlcpcb --download --use-exact-footprint C5815189`.
3. Retain its original TSX, OBJ and STEP bytes and hashes. Run:
   `python3 scripts/check_usb_locator_holes.py <candidate.tsx> --output <report.json>`.
   The screen accepts two explicit numeric locating holes of the specified
   diameter and pitch. Unsupported generated syntax requires native-output
   inspection rather than editing the component to pass.
4. Compare the complete footprint, both hole locations, plated slots, physical
   pin order and genuine CAD model against the manufacturer drawing. Passing
   this narrow screen alone is not full component approval.
5. Only after approval replace the board's unapproved candidate through normal
   source wiring, regenerate native artifacts and rerun applicable checks.
6. Resume publication in the same package, preserving partial-release recovery.

If the newest release still omits the hole, keep the part blocked and retain
an upstream reproduction report. Do not state that upgrading alone fixes it.
No upstream issue or message has been sent.
