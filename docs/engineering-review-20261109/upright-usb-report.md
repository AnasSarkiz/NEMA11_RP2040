# Upright USB-C qualification, existing NEMA11

Read-only study of reconstructed HEAD 7da9556d18d4e8b54cc790c58dd25d4b487f34eb; no board assets edited. Not manufacturing approval. Study commands used board-installed CLI 0.1.2446, tscircuit 0.0.3121 and Bun 1.4.4, with writable study-local XDG configuration. Original default configuration attempt failed read-only; corrected configuration location, no security change.

## Result

C5815189 / GCT USB4145-03-0070-C remains unqualified. A fresh supported `tsci import --jlcpcb --download --use-exact-footprint C5815189` succeeded. Current importer is NOT responsible for the oversized locator width: direct raw EasyEDA search and component reads succeeded HTTP 200, and the raw supplier NPTH path itself defines it. The earlier inability to distinguish supplier from importer responsibility is now resolved for this fresh sample.

Raw supplier path has straight span (4007.9918−4004.8422)×0.254 = 0.7999984 mm and semicircle radius 1.3976×0.254 =0.3549904 mm. Total capsule width 1.5099792 mm. Current native pill and exported NPTH G85 slot reproduce that exactly. Manufacturer A2 requires1.01×0.71 mm ±0.05, not1.51×0.71. The other locator isØ0.7099808; center pitch 7.999984 mm. Width is0.4999792 mm oversize nominal,0.4499792 above maximum drawing width.

The fresh TSX replaces the historical polygon with a native pill hole. Old project checker cannot parse that new syntax, and reports unsupported syntax rather than a complete native measurement; see direct fixture dist/usb/circuit.json and drill_npth.drl for definitive native/CAM evidence. The checker was not patched.

GCT's official A2 PCN explicitly says the recommended PCB layout changed for reliable pick-and-placement, making it inappropriate to dismiss this as merely extra clearance. Existing repo A2 drawing pages 1–2 were rendered and inspected. Direct current GCT drawing download returned403 and was not retried; official live product page and A2 PCN remain readable. The stored manufacturer PDF is A2 dated 31  January 2023. Do not use older A/A1 dualØ0.66-hole drawings as the target.

## Exact footprint and model observations

- 16 signal lands0.2999994×1.1500104 mm,0.50 mm pitch positions, two rows at y±1.479931 relative to import origin. Drawing row-center nominal 1.485 mm from0.86 mm inner gap and1.15 mm land length; ~0.005 mm discrepancy is inside±0.05 mm.
- 4 plated shell slots, rotated90°: actual horizontal drill1.0999978×0.5999988; copper1.5999968×1.0999978. Centers x−4.1999916/+3.7999924, y±1.429893. Matches nominal 8.00 × 2.86 pitch and1.10 × 0.60 drill/1.60 × 1.10 land dimensions within drawing tolerance.
- Native footprint bounds9.5999808×4.1098724; imported courtyard10.0999808×4.6098724, area 46.5596227 mm². Neither includes plugged-cable envelope.
- Manufacturer body is nominal 8.94 mm wide,3.16 mm shell depth and7.46 mm seated height; max lower lead span3.69 mm. 0070 shell stakes nominal 0.70 mm with drawing S tolerance+0.10/−0.20; locator pegsØ0.56±0.05 and0.64 mm depth. In 1.6 mm board these nominally do not project below bottom, but plated anchors still require validated soldering/inspection.
- Fresh OBJ/STEP outputs are unchanged relative to current imported model files (OBJ SHA25639f20ea318cd7eb64a56cd55d4d793922c83ebfdb6ce5314f968fcda7aee196e). Native model origin is(0.1974834,3.4270055,−4.5927208), board-surface anchor z0.8, no rotation. Raw OBJ z range−5.342732 to2.817271. Relative to supplied origin, top is7.4099918 mm and deepest stake−0.7500112 mm, whereas drawing seated height 7.46 and stake 0.70. This repeats the ~0.05 mm seating discrepancy; no manual pose correction performed. A section-based contact-plane review remains required before exact fit claims.
- Native importer does not provide from-above insertion metadata; native build emits a lateral-access warning for this genuine upright part. Do not 'fix' imported metadata manually under present constraints.

## Single-side assembly/process gate

Fixture native JSON emits 20 top paste apertures (16 signals plus 4 shell anchors) and 4 bottom paste apertures at anchors. The fresh official Gerber export confirms four flashes in B_Paste.gbr. This is a process qualification issue, not proof that all-top component placement or mixed SMT/THT assembly is impossible. All components on top is not yet evidence of a top-only stencil/reflow job. Requires supported upstream correction/configuration or assembler-approved shell-anchor process, plus review of top paste volume and slot fill. Do not manufacture with study CAM.

Official JLC catalog lists C5815189 as Extended, SMT Assembly, Economic and Standard, High assembly difficulty. Native build warns about potential JLC availability. Catalog eligibility does not guarantee order stock, stencil correctness, or that1.6 mm-board anchor soldering is approved. No stock reserved, no order or external contact made.

## Alternatives actually checked

- C5181332 / USB4145-03-0170-C: supported exact import reports component not found in EasyEDA library despite JLC listing. Not qualified.
- C5291559 / USB4145-03-0230-C: supported exact import succeeds. Locator polygon bounding box1.09982×0.7100316 mm,8 mm pitch. Width exceeds drawing maximum 1.06 by 0.03982 mm. Also2.3 mm nominal stakes project~0.7 mm below a1.6 mm board, before tolerances and solder. Not qualified, and not a clean replacement for low motor gap. Alternate checker report contains hardcoded C5815189 identity from legacy checker; filename/import are C5291559. No broad claim that all upright parts are impossible.

## Updated packing screen

Exact current dist/index circuit.json contains 89 fitted parts,16 top/73 bottom and 89 courtyard polygons. Sum of actual polygon areas765.793258 mm². Two flat USB courtyards 179.558787 mm² combined. Hypothetical two vertical USB courtyards 93.119245 mm² gives 679.353717 mm² total, saving 86.439541 mm².28 × 28 board minus four provisional R2.35 bolt-head disks gives 714.602218 mm², leaving 35.248501 mm².

This is only an area screen, not packing, placement, or routing proof. It excludes optional DNP encoder courtyard reservation, required routing/vias/power widths, edge setbacks, cable overmolds, assembler access and validated fastener keepouts. Courtyard sum itself is not a physical impossibility theorem because shapes/allowed overlaps/overhang and process clearances need their own rules. Old818.76 mm² sum is not reproduced by the current native geometry and should not be reused. Native component-bound sums are a different metric and must not be mixed with courtyard sums. No all-top placement trial was attempted because no upright footprint has qualified.

## Minimum next steps

1. Obtain supported supplier correction for C5815189 locator width and investigate supported model seating/paste/insertion metadata. Reimport untouched and compare drawing, native JSON, drills, paste and model contacts again. Or qualify a different JLC-importable upright connector against its exact manufacturer drawing.
2. Validate one-top-side assembly process for shell anchors, package stock, and stencil/reflow capability with assembler when authorized.
3. Then actual all-top placement/routing trial on same28 × 28 board, preserving required buzzer, original bolt axes and optional centered encoder reservation. Include two plugs, cable exit and screw/tool access in 3D.
4. Verify motor standoff/thread engagement/insulation and board underside stakes against actual motor. Preserve current two-adjacent-edge fallback until all gates pass.

## Evidence and sources

- geometry-results.json and analyze.py: reproducible current courtyard arithmetic, native hole/paste summary.
- import.log, build.log, gerbers.log, usb.circuit.tsx, dist/usb/circuit.json, usb-gerbers.zip: fresh supported output.
- raw-supplier-search.json, raw-supplier-component.json: source data confirming oversized path.
- imports/: untouched supported outputs; source JLCEDA/EasyEDA official library, https://easyeda.com and https://lceda.cn .
- https://gct.co/connector/usb4145
- https://gct.co/files/pcns/gct%20usb4145%20a2%20pcn%2020230214.pdf
- https://jlcpcb.com/partdetail/6744750-USB4145_03_0070C/C5815189
- https://jlcpcb.com/partdetail/5839804-USB4145_03_0170C/C5181332
- https://jlcpcb.com/partdetail/6035042-USB4145_03_0230C/C5291559
