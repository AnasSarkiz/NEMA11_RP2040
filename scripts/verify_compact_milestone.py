#!/usr/bin/env python3
"""Gate the compact placement milestone on exact native artifact identities."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/compact-controller'
def read(name):return json.loads((OUT/name).read_text())
def sha(name):return hashlib.sha256((OUT/name).read_bytes()).hexdigest()
source=sha('unrouted.circuit.json');checks={}
for name in ['source-build.json','electrical-parity.json','placement-verification.json','nominal-assembly-audit.json','3d-export-verification.json']:
 d=read(name);assert d['circuit_sha256']==source,name
 if name=='nominal-assembly-audit.json':
  assert d['nominal_solid_and_lead_fit_pass'] and d['whole_fitted_parts_within_28_3mm_frame'] and d['all_fitted_on_top']
  assert len(d['errors'])==2 and all('invalid_original_supplier_STEP' in e and e['part'] in ['J_PD','J_DATA'] for e in d['errors'])
 else:assert not d.get('errors',d.get('render_errors',[])),name
 checks[name]=sha(name)
p=read('placement-verification.json');assert p['placement_pass'] and not p['physical_routing_complete']
assert p['components']==92 and p['fitted_parts']==82 and p['original_supplier_pad_geometries_verified']==340
assert p['nominal_component_spacing_pairs_checked']==2346
schematic=read('schematic-verification.json');assert schematic['passed'] and schematic['source_sha256']==source and schematic['schematic_sha256']==sha('schematic.circuit.json')
assert schematic['physical_pins']==340 and schematic['explicit_NC_pins']==36 and schematic['sheet_count']==6
pdf=read('pdf-verification.json');assert pdf['pdf_sha256']==sha('schematic-a4.pdf') and pdf['schematic_sha256']==schematic['schematic_sha256'] and pdf['page_count']==6
for c in read('native-source-checks.json'):
 assert c['exit_code']==0 and c['input_sha256']==hashlib.sha256((ROOT/c['input']).read_bytes()).hexdigest()
for name in ['schematic-verification.json','pdf-verification.json','native-source-checks.json']:checks[name]=sha(name)
models=read('3d-export-verification.json');assert models['glb_sha256']==sha('development-controller.glb')
for a in models['original_supplier_assets_loaded']:assert hashlib.sha256((ROOT/a['path']).read_bytes()).hexdigest()==a['sha256']
carrier=json.loads((ROOT/'artifacts/requirements/compact-front-carrier-proposal.json').read_text());assert carrier['within_28_3mm_frame_XY'] and carrier['nominal_motor_intersection_mm3']<1e-5 and not carrier['motor_rear_holes_or_shaft_assumed']
report={'scope':'Validated native 28 mm full-controller placement and six-sheet schematic milestone; UNROUTED','source_sha256':source,'schematic_sha256':schematic['schematic_sha256'],'checked_artifacts':checks,'placement_and_schematic_pass':True,'physical_routing_complete':False,'zero_opens_or_full_routed_DRC_claimed':False,'manufacturing_release':False,'limitations':['Compact routing remains incomplete; construction file has opens','Nominal supplier models and 5 um minimum JLC spacing surplus are not tolerance-qualified','Original GCT STEP compound validity limitation retained','Carrier corner radii, narrow-rail strength, fasteners, harness and machine interface are unqualified','Buzzer waveform/current/reflow, motor current accuracy, thermal/regen behavior, JLC stackup/process/panel and stock remain unqualified']}
(OUT/'milestone-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['checked_artifacts','limitations']}))
