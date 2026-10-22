# C5815189 released-import gate

The user's requirement is a corrected tscircuit release and supported fresh
JLCPCB import, without locally patching any purchased component definition.

CLI 0.1.2400 with tscircuit 0.0.3003 was installed and the part re-imported. It
still fails the manufacturer-geometry gate: the second locator is now a polygon
cutout approximately 0.80 × 0.71 mm with inward-pinched sides. The manufacturer's
page-2 drawing requires one Ø0.71 mm round hole plus one 1.01 × 0.71 mm horizontal
slot at 8 mm spacing. Earlier wording calling for two circles was incorrect.

The corrected read-only regression screen checks the circular hole, polygon
slot bounds, spacing and clearance for the minimum slot interior at drawing
tolerance. Both the original missing-slot output and the new malformed-slot
output fail. Unsupported source syntax requires native-output inspection.

See `docs/import-refresh-20261022.md`, the exact import manifest, manufacturer
PDF and native review fixture for reproduction. No component geometry, pins or
CAD pose is patched. Keep C5815189 excluded until a released supported import
passes the complete drawing review. C165948 remains an unapproved alternate.
No upstream issue or message has been sent.
