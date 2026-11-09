# Nominal underside model envelope, NEMA11 fallback

Reviewed 2026-11-09 UTC against reconstructed commit `7da9556`. This is a
read-only mesh measurement of the existing two-sided fallback, not a motor-fit
or assembly approval. No source, import, placement or native JSON was changed.

## Result

All 89 fitted CAD records load through the official
`circuit-json-to-gltf` 0.0.164 `loadCadComponentMesh` API. The independent
analytic Z calculation agrees with that loader to less than 1e-8 mm for every
record. All model sources are local imported OBJ files. Model paths/hashes,
native-input hash and per-part bounds are preserved in `height-audit.json`.

Greatest nominal projection below the PCB's bottom surface:

| Part | Placement | Imported mesh projection |
| --- | --- | ---: |
| L_BUCK, SRN4018-4R7M C780206 | Bottom | 1.830 mm |
| U_ESD, USBLC6-2SC6 C2687116 | Bottom | 1.649 mm |
| D_PD and D_DATA | Bottom | 1.450 mm |
| J_MOTOR, B4B-PH-K-S C131334 | Top, through-hole tails | 1.400 mm |
| C_BUCK_IN and output capacitors | Bottom | 1.300 mm |

These values follow the imported model's own origin and native transform. They
are not manufacturer maximum package heights. Supplier mesh/origin errors,
solder, part tolerances, board bow, insulation, fastener stackup and the motor's
rear features are not included. Models must be checked against exact delivered
parts and drawings before determining a safe gap.

If an uninterrupted motor plane occupied the same XY region beneath the
inductor, the nominal imported mesh alone would require more than 1.83 mm
clearance from the PCB bottom. A hypothetical 2.0 mm gap would leave only
0.17 mm beyond that model, before all the omitted allowances. The earlier
2 mm preview gap is not an approved mounting dimension or evidence of fit.

Top-side-only component placement would still not make the underside flat:
the retained motor header has modeled tails about 1.4 mm below the board.
This observation does not decide whether those tails can be trimmed, soldered
or accommodated. No such process or modification has been qualified.

## Method and reproduction

`verify_official_loader.mjs` loads the original unmodified CAD records and PCB
context through the official world-coordinate mesh API. It passes the local
board directory as a file URL, performs no network model fetch, rejects any
nonlocal import URL and checks that input objects remain unchanged. Native
world Z is +up, PCB surfaces are ±0.8 mm for the 1.6 mm board.

Run with the board's installed Bun 1.4.4 executable:

    <board>/node_modules/.bin/bun verify_official_loader.mjs <board>
    python3 audit_height.py --board <board> --official official-loader-bounds.json --output height-audit.json
    python3 -m unittest discover -s . -p test_height.py -v

The analytic check explicitly rejects model scaling, box fitting, alternate
normal axes, arbitrary X/Y rotations and unsupported surface offsets. It uses
the authored model origin and top/bottom sign; Z rotations do not change height.
Three regressions cover top-side through-hole tails, bottom origin/height and
unsupported transforms. All pass. This is not a general CAD collision checker.

Node 24's built-in fetch cannot load file URLs, so the initial Node attempt
failed before loading a model. Bun's supported file-URL loader succeeded. No
network proxy, fetch override or production-library patch was used.

Exact native input SHA-256:
`b93b921adc556e840dee2bc4acb0d4f2de8fe990ebf6b6a2638e4636379acf51`.
Installed transformation logic inspected in `circuit-json-to-gltf/dist/index.js`
(`loadCadComponentBox`, `getMeshOrigin`, `loadCadComponentMesh`) and core's CAD
record generation. Hardware qualification remains separate from consistency
between two calculations of the same imported model.
