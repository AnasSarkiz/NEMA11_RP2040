# Reproduce and inspect this frozen study

This is a standalone evidence package, not a board revision or release candidate. Do not order its diagnostic Gerbers. No board edits or upstream publication occurred. Imported component files are byte-for-byte original supported imports. No credentials, CLI config, dependencies, cache, or symlinks are included.

## Offline arithmetic and integrity

From this directory:

```sh
sha256sum -c SHA256SUMS
python3 analyze.py --output /tmp/upright-recalculated.json
cmp geometry-results.json /tmp/upright-recalculated.json
```

The defaults refer only to included `inputs/current-board-circuit.json` and `dist/usb/circuit.json`. Alternate inputs are explicitly selectable:

```sh
python3 analyze.py --board-json /path/to/current-native.json --usb-json /path/to/usb-native.json --output /tmp/other-analysis.json
```

PROVENANCE.json binds the exact included native input SHA-256 to the study's Git HEAD and tool versions. The native file was copied from the existing board's dist/index/circuit.json; this freeze does not claim a new whole-board rebuild. The single-USB fixture was freshly built in the study.

## Fresh supported build/CAM replay

Use an existing trusted installation with Bun 1.4.4, @tscircuit/cli 0.1.2446 and tscircuit 0.0.3121 available through PATH/module resolution. Dependencies are deliberately not included. Work on a copy of this frozen directory and retain this evidence unchanged. The study used the board installation's node_modules for dependency resolution; a fresh replay must provide its own compatible dependency installation. Put temporary CLI state in a writable directory:

```sh
export XDG_CONFIG_HOME="$(mktemp -d)"
tsci build usb.circuit.tsx --pcb-svgs
tsci export usb.circuit.tsx --format gerbers -o usb-gerbers-replay.zip
```

Build/export logs and emitted native output are included. Replayed timestamps and availability warnings may differ. Inspect `dist/usb/circuit.json`, `cam/drill_npth.drl`, `cam/drill-L1-L2.drl`, `cam/F_Paste.gbr` and `cam/B_Paste.gbr`.

## Original external operations, for documentation only

These already ran during the study; archival packaging did not repeat imports or network calls. Network/service changes may affect future results. Run imports in a new empty study directory, never over the frozen originals or reviewed board imports:

```sh
tsci import --jlcpcb --download --use-exact-footprint C5815189
tsci import --jlcpcb --download --use-exact-footprint C5181332
tsci import --jlcpcb --download --use-exact-footprint C5291559
```

C5815189 and C5291559 succeeded. C5181332 returned component not found; its failure log is included. Raw EasyEDA component evidence was fetched by POST to https://easyeda.com/api/components/search with form fields type=3, doctype[]=2, uid=0819f05c4eef4c71ace90d822a990e87, returnListStyle=classifyarr, wd=C5815189, version=6.4.7, then GET https://easyeda.com/api/components/593c7880a0f24a6f956e247e84bdfa3b?version=6.4.7&uuid=593c7880a0f24a6f956e247e84bdfa3b&datastrid= . Both returned HTTP 200; exact response JSON is included. Raw supplier SOLIDREGION NPTH geometry establishes the oversized capsule before import.

## Legacy checker limitation

`legacy_check_usb_locator_holes.py` is an unchanged copy of the board checker. The included fresh-locator.json reports unsupported pill-hole syntax, so it is not the definitive measurement of the new import. Native JSON and CAM provide that measurement. The alternate0230-locator.json has a legacy hardcoded C5815189 identity despite testing the C5291559 file, as noted in REPORT.md. Its geometric measurements remain inspectable, but do not treat its identity fields as alternate-part identification.

## Archive boundaries

Original manufacturer A2 drawing and rendered pages are included. The PCN is retained as dated source/extraction evidence, not original PCN PDF bytes. The unsuccessful current drawing download's HTTP 403 body is retained as HTML. SHA256SUMS covers every regular evidence file except itself. The enclosing tar.gz has its own separate SHA-256 sidecar. No symlinks are permitted in the archive.
