#!/usr/bin/env python3
"""Gate only the connected clock/USB escapes, never full controller routing."""
import hashlib,json,math
from pathlib import Path
from pcb_geometry import Copper
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/compact-escape'
def read(name):return json.loads((OUT/name).read_text())
def sha(name):return hashlib.sha256((OUT/name).read_bytes()).hexdigest()
source=sha('unrouted.circuit.json');board=sha('board.circuit.json')
for name in ['source-build.json','electrical-parity.json','placement-verification.json','nominal-assembly-audit.json']:
 r=read(name);assert r['circuit_sha256']==source,name
 if name=='nominal-assembly-audit.json':
  assert r['nominal_solid_and_lead_fit_pass'] and r['whole_fitted_parts_within_28_3mm_frame'] and r['all_fitted_on_top']
  assert len(r['errors'])==2 and all('invalid_original_supplier_STEP' in e and e['part'] in ['J_PD','J_DATA'] for e in r['errors'])
 else:assert not r.get('errors',r.get('render_errors',[])),name
assert read('placement-verification.json')['placement_pass']
schematic=read('schematic-verification.json');assert schematic['passed'] and schematic['physical_pins']==340 and schematic['sheet_count']==6
assert schematic['source_sha256']==source and schematic['schematic_sha256']==sha('schematic.circuit.json')
pdf=read('pdf-verification.json');assert pdf['page_count']==6 and pdf['schematic_sha256']==schematic['schematic_sha256'] and pdf['pdf_sha256']==sha('schematic-a4.pdf')
for check in read('native-source-checks.json'):
 assert check['exit_code']==0 and check['input_sha256']==hashlib.sha256((ROOT/check['input']).read_bytes()).hexdigest()
clock=read('clock-layout-audit.json');assert clock['clock_construction_pass'] and clock['source_sha256']==source and clock['circuit_sha256']==board
audit=read('independent-copper-audit.json');assert audit['circuit_sha256']==board
assert audit['errors'] and all(e['type']=='disconnected_net' for e in audit['errors']), 'Copper defects must not be hidden among expected unfinished nets'
assert len(audit['errors'])==58
native=read('native-drc.json');assert native['circuit_sha256']==board and native['strict_schema_pass']
assert not native['native_drc_pass'] and len(native['errors'])==270
assert all(e['type']=='pcb_port_not_connected_error' for e in native['errors'])
c=Copper(read('board.circuit.json'));usb=[]
for name,pin in [('MCU_DP',47),('MCU_DM',46)]:
 key=next(k for k,n in c.nets.items() if n==name);members,roots=c.groups(key)
 physical={r for (e,_,_),r in zip(members,roots) if e['type'] in ['pcb_smtpad','pcb_plated_hole']}
 traces=[e for e in c.records if e['type']=='pcb_trace' and c.key(e)==key]
 assert len(physical)==1 and traces
 assert not any(e['type']=='pcb_via' and c.key(e)==key for e in c.records)
 length=0
 for trace in traces:
  assert all(p['route_type']=='wire' and p['layer']=='top' and p['width']>=.16 for p in trace['route'])
  length+=sum(math.dist((a['x'],a['y']),(b['x'],b['y'])) for a,b in zip(trace['route'],trace['route'][1:]))
 assert length<3.0
 usb.append(dict(net=name,MCU_pin=pin,total_trace_mm=length,layers=['top'],signal_vias=0,physical_pad_islands=1))
assembly=read('assembly-geometry-verification.json');assert assembly['passed'] and assembly['native_models_checked']==84 and assembly['GLB_sha256']==sha('development-assembly.glb')
assert read('assembly-build.json')['source_sha256']==board
export=read('assembly-3d-export-verification.json');assert export['circuit_sha256']==sha('assembly.circuit.json') and export['glb_sha256']==assembly['GLB_sha256']
report=dict(scope='Validated 28 mm all-top placement, schematic, native 3D, crystal and short MCU USB escapes ONLY',source_sha256=source,board_sha256=board,assembly_sha256=sha('assembly.circuit.json'),native_assembly_GLB_sha256=assembly['GLB_sha256'],usb_escape_connections=usb,USB_pair_impedance_and_complete_data_path_qualified=False,independent_copper_short_clearance_drill_edge_defects=0,disconnected_controller_nets=58,native_DRC_pass=False,native_port_connectivity_findings=270,all_fitted_components_on_top=True,nominal_fitted_models_within_28_3mm_frame=True,full_controller_routing_complete=False,manufacturing_release=False)
(OUT/'escape-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
