# Registry access and original-source milestone, 2026-10-17

The native tscircuit CLI now authenticates as `@AnasSarkiz`. The cloud runtime
reports unrestricted, enforced Internet access. A second token is unnecessary.
Credentials are held in the CLI's private configuration outside this repository;
no credential or authorization URL is included in source or review artifacts.

## Published MCU subsystem prototype

[AnasSarkiz/NEMA11_RP2040_MCU_Prototype v0.1.0](https://tscircuit.com/AnasSarkiz/NEMA11_RP2040_MCU_Prototype)
is a separate **MCU-only development prototype**, not the complete controller.
The [publication receipt](../artifacts/publication/mcu-prototype-0.1.0.json)
records its release ID and independent byte-for-byte downloads of all seven
required source/build files. The public page and registry-generated native 3D
preview also respond successfully. The native CLI reported HTTP 413/500 upload
errors, but the actual release and exact files were persisted; remote file
verification establishes the result independently of its exit status.

`prototypes/rp2040-core/package-verification.json` is the frozen pre-upload
build receipt. Its `registry_published: false` field describes that pre-upload
snapshot. The separate post-upload receipt above records the verified release.
The prepared package's native Circuit JSON, source/build and checks remain
unchanged by publication. No manufacturing release is implied.

## Exact NEMA14 reference

The exact published `AnasSarkiz/NEMA14_RP2040@1.13.0` release is
`b28fdf86-c142-4a22-b03c-3719461c092c`. Its 516 files, totaling about 79 MB,
were downloaded into a read-only reference-materials cache; the NEMA14 GitHub
repository was not modified. The [complete file/hash manifest](../references/manifests/nema14-v1.13.0.json)
and [component inventory](../artifacts/requirements/reference-1.13-inspection.json)
identify the source. It contains 92 components and 343 physical source ports,
including genuine CH224A C42459160 and its 56 kΩ 15 V configuration resistor.
The older v1.12 inspection is historical evidence rather than the new baseline.

The existing MCU subset has the same 119 physical pin-to-net connections and
matching part numbers/resistor/capacitor values in v1.13. A strict metadata
comparison records one omission: its generic imported crystal chip does not
carry the reference's numeric `frequency: 12000000` field. Its unchanged
ABM8-272-T3 supplier part and manufacturer drawing establish 12 MHz, but this
metadata omission remains explicit in the [comparison report](../artifacts/requirements/core-reference-1.13-parity.json).
Full-controller parity is not yet established.

## Original motor evidence

The original PDF and STEP now download with a standard browser User-Agent.
The PDF is drawing A0071, title revision 2, dated 2026-06-18. Source URLs, hashes
and nominal STEP bounds are retained in [motor-originals.json](../artifacts/requirements/motor-originals.json).
The original STEP is retained unchanged in `imports/motor/`.

Verified drawing facts include 0.67 A/phase, 5.60 Ω ±10% at 25 °C, 4.00 mH ±20%
at 1 kHz, 28.3 mm maximum frame, 33 mm maximum body, 23 ±0.15 mm front pitch,
and four front M2.5 threads with 3.5 mm minimum depth. The front shaft is
Ø5 +0/−0.012 mm and projects 20 ±1 mm; the front pilot is Ø22 +0/−0.05 mm.
The leads are 300 ±10 mm AWG26 UL1569, ordered black A+, green A−, red B+, blue B−.
Ambient range is −10 to 50 °C and the drawing states an 80 °C maximum rise.
None of this authorizes rear motor mounting holes or a rear shaft.

The genuine STEP is valid and contains five solids. Its total bounds include
short modeled wire stubs and the front shaft, so those overall bounds must not
be mistaken for the motor's specified maximum body size. Nominal CAD is not a
maximum tolerance envelope or proof of threaded rear attachment.

At 0.67 A in both coils, drawing resistance gives approximately 5.028 W copper
loss at 25 °C, or 5.530 W at maximum resistance tolerance. The calculation now
also distinguishes ideal sine microstepping loss from two-coil DC excitation.
Winding heating and actual driver junction temperature remain unqualified.
The candidate current divider is still an engineering screen, not a qualified
current-accuracy guarantee or final supplier selection.

## Remaining design work

The reference's JST SH terminal specification accepts AWG32–28, whereas this
motor has AWG26 leads. Directly crimping those motor leads into SH terminals is
not an approved termination. The full design needs a compatible genuine JST
connector/terminal set or a fully specified transition harness; no strand
removal or unqualified wire crimp is accepted. Live search results observed
so far include unrelated components, so they do not establish part identity
or stock. Mechanical attachment, final copper, full schematics/ERC, BOM/CPL,
thermal/fabrication checks and the complete native motor assembly remain open.
