#!/usr/bin/env python3
"""Freeze the committed routed native assembly as its own immutable prototype."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'prototypes/controller-pcb-0.3.0'
path=ROOT/'artifacts/controller/assembly.circuit.json'
proof=json.loads((ROOT/'artifacts/controller-pcb/milestone-verification.json').read_text())
assert proof['milestone_passed'] and not proof['manufacturing_release']
assert proof['assembly_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
revision=subprocess.check_output(['git','log','-1','--format=%H','--',str(path.relative_to(ROOT))],cwd=ROOT,text=True).strip()
assert subprocess.check_output(['git','show',revision+':'+str(path.relative_to(ROOT))],cwd=ROOT)==path.read_bytes()
records=json.loads(path.read_text())
assert sum(e['type']=='source_component' for e in records)==94
assert sum(e['type']=='source_port' for e in records)==341
assert sum(e['type']=='schematic_sheet' for e in records)==6
assert sum(e['type']=='cad_component' for e in records)==84
serialized=(json.dumps(records,separators=(',',':'))+'\n').encode()
receipt=ROOT/'artifacts/publication/controller-prototype-0.3.0.json'
if receipt.exists() and json.loads(receipt.read_text())['registry_published']:
    assert (OUT/'index.circuit.json').read_bytes()==serialized,'Published snapshots are immutable'
    print('Published 0.3.0 unchanged; preserving package metadata.')
    raise SystemExit(0)
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'index.circuit.json').write_bytes(serialized)
package={'name':'@tsci/AnasSarkiz.NEMA11_RP2040_Controller_Prototype','version':'0.3.0',
         'description':'Routed NEMA11 controller, six schematics and OEM motor/front-carrier native assembly; development prototype, NOT fabrication released',
         'main':'index.circuit.json','type':'module','private':False,
         'repository':{'type':'git','url':'https://github.com/AnasSarkiz/NEMA11_RP2040.git'}}
(OUT/'package.json').write_text(json.dumps(package,indent=2)+'\n')
(OUT/'tscircuit.config.json').write_text(json.dumps({'includeBoardFiles':['index.circuit.json'],'previewComponentPath':'index.circuit.json'},indent=2)+'\n')
verification={'package':package['name'],'version':'0.3.0','source_milestone_commit':revision,
              'source_repository':package['repository']['url'],'source_path':str(path.relative_to(ROOT)),
              'scope':'Routed full electrical PCB and six-sheet schematic, unchanged OEM motor and original front carrier proposal',
              'circuit_sha256':hashlib.sha256(serialized).hexdigest(),
              'source_PCB_sha256':proof['circuit_sha256'],
              'source_components':94,'PCB_components':92,'physical_ports':341,'schematic_sheets':6,'fitted_CAD_models':84,
              'independent_copper_connectivity_clock_USB_ground_reference_shorts_CAM_verified':True,
              'raw_native_DRC_errors':36,'native_errors_review':'Individually checked circular-keepout bounding-rectangle approximations',
              'registry_published':False,'manufacturing_release':False,
              'limitations':['Actual harness, mating plug/contacts and purchased fasteners absent',
                             'Motor AWG26 insulation OD and PH crimp qualification unresolved',
                             'Original GCT USB STEP compound validity limitation retained',
                             'Factory stackup/impedance, thickness, via-fill, stencil/panel and assembly process acceptance pending',
                             'Current accuracy, heat, regeneration and physical operation unqualified; stock unreserved']}
(OUT/'package-verification.json').write_text(json.dumps(verification,indent=2)+'\n')
(OUT/'README.md').write_text('''# NEMA11 RP2040 routed controller prototype 0.3.0

**Validated development milestone. Not fabrication released.**

Native tscircuit Circuit JSON contains the routed 35 × 40 mm, four-layer controller,
all 92 electrical components and 341 physical terminals, six functional schematic
sheets, 82 fitted genuine supplier models, the unchanged STEPPERONLINE 11HS12-0674S
motor and an original front-anchored carrier proposal. No rear shaft or mounting
holes are invented. Original 0.1.0 and 0.2.0 source snapshots remain immutable.

The design preserves the exact published NEMA14 v1.13.0 features: RP2040, flash,
crystal, boot/SWD, separate USB-C data and 15 V PD, CH224A/ADC/POWER_GOOD, A4988
and both sense paths, 1/16 microstepping, RGB/power indication, buzzer, temperature,
regulators, protection, test points and optional encoder with both capacitors DNP.
Explicit changes are a 20 kΩ VREF resistor, genuine 1/3 W 0.24 Ω shunts and a
through-hole JST PH header. Manufacturer-required USB locating holes are corrected
in the wrapper while supplier originals remain preserved.

The PCB has 554 traces, 334 vias (minimum 0.45/0.30 mm), 12 component plated holes/
slots and eight NPTH. Independent physical connectivity, shorts, clearances,
clock routing, USB ground reference, every-trace/layer policy and actual CAM
round-trip checks pass. All 36 retained native DRC findings are individually
verified bounding-rectangle approximations of circular keepouts; raw diagnostics
are retained in GitHub. Nine supplier pin metadata warnings remain documented.

The nominal native assembly has no solid interference. All 84 exported model
bounds are independently checked. The original GCT STEP compound's OCCT validity
limitation remains visible. Complete harness, genuine mating plug/contacts and
purchased fasteners are absent. Conditional tool/plug envelopes are procurement
constraints, not physical assembly qualification.

The ideal peak trip is 0.572917 A before routed sense resistance; driver accuracy
at this VREF is not guaranteed. Factory-approved stackup/90 Ω USB impedance,
1 oz on every layer, actual PCB thickness ≤1.60 mm or JST acceptance, filled/capped
vias, stencil, panel/assembly process, stock, wire insulation OD/crimp qualification,
current/thermal/regeneration and physical operation remain unresolved. Do not order
this milestone as a released production assembly.

Open with `tsci dev index.circuit.json`; build with `tsci build index.circuit.json`.
The canonical source and exact review Gerbers, 81-placement JLC SMT BOM/CPL,
manual assembly list, six-page A4 PDF, native GLBs and independent reports are in
[NEMA11_RP2040](https://github.com/AnasSarkiz/NEMA11_RP2040).
See [manufacturing requirements](https://github.com/AnasSarkiz/NEMA11_RP2040/blob/main/docs/manufacturing-requirements.md).
`package-verification.json` is the pre-upload source receipt; GitHub publication
artifacts independently verify the uploaded bytes.
''')
print('Staged native routed controller assembly prototype 0.3.0 from '+revision)
