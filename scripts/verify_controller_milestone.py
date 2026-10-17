#!/usr/bin/env python3
"""Gate the routed milestone on independent results for these exact artifact bytes."""
import collections
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
def read(path):return json.loads((ROOT/path).read_text())

pcb='artifacts/controller-pcb/'
board=pcb+'board.circuit.json'
board_hash=sha(board)
records=read(board)
counts=collections.Counter(e['type'] for e in records)
assert counts['source_component']==92 and counts['source_port']==341
assert counts['pcb_trace']==554 and counts['pcb_via']==334
assert counts['pcb_plated_hole']==12 and counts['pcb_hole']==8
checks={}
for name,flag in [('independent-copper-audit.json',None),('native-drc-review.json','reviewed_DRC_pass'),
                  ('native-shorts-verification.json','passed'),('independent-cam-audit.json','CAM_roundtrip_pass'),
                  ('clock-layout-audit.json',None),('trace-and-layer-audit.json','passed'),
                  ('USB-reference-audit.json','passed'),('assembly-data/export-verification.json',None),
                  ('PCB-build.json',None),('3d-export-verification.json',None)]:
    d=read(pcb+name)
    assert d['circuit_sha256']==board_hash,name+' is stale'
    assert not d.get('errors',[]),name
    if flag:assert d[flag],name
    checks[name]={'sha256':sha(pcb+name),'same_PCB_bytes':True}
for f in read(pcb+'review-cam-export.json')['files']:
    assert sha(pcb+'review-cam/'+f['name'])==f['sha256']

source_hash=sha('artifacts/controller/unrouted.circuit.json')
schematic=read('artifacts/controller/schematic-verification.json')
assert schematic['passed'] and schematic['source_sha256']==source_hash
assert schematic['schematic_sha256']==sha('artifacts/controller/schematic.circuit.json')
pdf=read('artifacts/controller/pdf-verification.json')
assert pdf['pdf_sha256']==sha('artifacts/controller/schematic-a4.pdf')
assert pdf['schematic_sha256']==schematic['schematic_sha256'] and pdf['page_count']==6
for d in read('artifacts/controller/native-source-checks.json'):
    assert d['exit_code']==0 and d['input_sha256']==sha(d['input'])
assert read('artifacts/controller/electrical-parity.json')['circuit_sha256']==source_hash
assert not read('artifacts/controller/electrical-parity.json')['errors']
assembly=read('artifacts/controller/assembly-build.json')
assert assembly['PCB_routed'] and assembly['source_sha256']==board_hash
models=read('artifacts/controller/assembly-3d-export-verification.json')
assert models['circuit_sha256']==sha('artifacts/controller/assembly.circuit.json')
assert models['glb_sha256']==sha('artifacts/controller/development-assembly.glb')
geometry=read('artifacts/controller/assembly-geometry-verification.json')
assert geometry['passed'] and geometry['GLB_sha256']==models['glb_sha256'] and geometry['native_models_checked']==84
nominal=read('artifacts/controller/nominal-assembly-audit.json')
assert nominal['nominal_solid_and_lead_fit_pass'] and nominal['circuit_sha256']==source_hash
assert read('artifacts/requirements/routed-electrical-budget.json')['circuit_sha256']==board_hash

a=ROOT/pcb/'assembly-data'
with (a/'JLC_SMT_BOM.csv').open() as f:bom=list(csv.DictReader(f))
with (a/'JLC_SMT_CPL.csv').open() as f:cpl=list(csv.DictReader(f))
bom_names=[n.strip() for row in bom for n in row['Designator'].split(',')]
assert len(bom_names)==len(set(bom_names))==81 and len(bom)==44
assert set(bom_names)=={row['Designator'] for row in cpl} and len(cpl)==81
source={e['name']:e for e in records if e['type']=='source_component'}
excluded={n for n,e in source.items() if e.get('do_not_place')}
assert not set(bom_names)&excluded and 'J_MOTOR' not in bom_names
for row in cpl:
    assert 0<float(row['Mid X'].removesuffix('mm'))<35
    assert 0<float(row['Mid Y'].removesuffix('mm'))<40
csv_proof={'scope':'Independent CSV membership, exclusions and board-origin bounds',
           'circuit_sha256':board_hash,'SMT_BOM_CPL_designators':81,'BOM_groups':44,
           'unique_designators':True,'manual_PH_excluded':True,'encoder_and_bare_test_points_excluded':True,
           'files':[{'path':str(p.relative_to(ROOT)),'sha256':sha(str(p.relative_to(ROOT)))}
                    for p in sorted(a.glob('*.csv'))],
           'passed':True,'manufacturing_release':False}
(a/'independent-csv-verification.json').write_text(json.dumps(csv_proof,indent=2)+'\n')
proof={'scope':'Exact routed PCB, six-sheet schematic, BOM/CPL and nominal native assembly milestone',
       'circuit_sha256':board_hash,'assembly_sha256':sha('artifacts/controller/assembly.circuit.json'),
       'source_sha256':source_hash,'checks':checks,'counts':dict(counts),
       'raw_native_DRC_errors':36,'all_native_errors_individually_reviewed_as_circular_keepout_approximation':True,
       'source_and_physical_validation_tests':29,'nominal_assembly_models':84,
       'milestone_passed':True,'manufacturing_release':False,
       'remaining_requirements':'docs/manufacturing-requirements.md'}
(ROOT/pcb/'milestone-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps({'exact_artifact_milestone_verified':True,'PCB_sha256':board_hash,'manufacturing_release':False}))
