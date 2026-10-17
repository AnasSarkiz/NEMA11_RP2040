#!/usr/bin/env python3
"""Verify the new four-hole source milestone; never a routing/fabrication gate."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/compact-four-mounts'
def check_mounts(records,config):
 errors=[]
 holes=[e for e in records if e['type']=='pcb_hole' and not e.get('pcb_component_id')]
 actual=sorted((round(h['x'],6),round(h['y'],6),round(h['hole_diameter'],6)) for h in holes)
 wanted=sorted((m['x'],m['y'],m['diameter']) for m in config['mounts'])
 if len(holes)!=4 or actual!=wanted:errors.append({'four_mount_geometry':actual,'expected':wanted})
 keepouts=[e for e in records if e['type']=='pcb_keepout']
 for m in config['mounts']:
  found=[k for k in keepouts if k['shape']=='circle' and abs(k['center']['x']-m['x'])<1e-6 and abs(k['center']['y']-m['y'])<1e-6 and abs(k['radius']-m['radius'])<1e-6]
  if len(found)!=1 or set(found[0]['layers'])!={'top','inner1','inner2','bottom'}:errors.append({'missing_four_layer_head_keepout':[m['x'],m['y']]})
 return errors

def main():
 def read(f):return json.loads((OUT/f).read_text())
 def sha(f):return hashlib.sha256((OUT/f).read_bytes()).hexdigest()
 source=sha('unrouted.circuit.json');records=read('unrouted.circuit.json')
 config=json.loads((ROOT/'config/compact-four-mounts.json').read_text())
 assert not check_mounts(records,config)
 names={e['name'] for e in records if e['type']=='source_component'}
 assert len(names)==86 and not names.intersection(config['omitted_components'])
 assert sum(e['type']=='source_port' for e in records)==326
 for f in ['source-build.json','electrical-parity.json','placement-verification.json']:
  d=read(f);assert d['circuit_sha256']==source,f
  assert not d.get('errors',d.get('render_errors',[])),f
  assert not d.get('schema_errors',[]),f
 placement=read('placement-verification.json')
 assert placement['placement_pass'] and placement['all_fitted_on_top'] and placement['fitted_parts']==76
 assert len(placement['PCB_mounts'])==4 and all(m['head_within_28_3mm_frame'] and m['hole_edge_to_PCB_edge_mm']>=.6-1e-6 for m in placement['PCB_mounts'])
 schematic=read('schematic-verification.json')
 assert schematic['passed'] and schematic['source_sha256']==source and schematic['schematic_sha256']==sha('schematic.circuit.json')
 assert schematic['physical_pins']==326 and schematic['explicit_NC_pins']==36
 pdf=read('pdf-verification.json');assert pdf['page_count']==6 and pdf['pdf_sha256']==sha('schematic-a4.pdf') and pdf['schematic_sha256']==sha('schematic.circuit.json')
 for c in read('native-source-checks.json'):
  assert c['exit_code']==0 and c['input_sha256']==hashlib.sha256((ROOT/c['input']).read_bytes()).hexdigest()
 report=dict(scope='Four-corner native compact source, supplier-pad placement and connected A4 schematic checkpoint only',source_sha256=source,schematic_sha256=sha('schematic.circuit.json'),PCB_mount_count=4,PCB_mount_pitch_mm=25,PCB_hole_diameter_mm=1.8,source_components=86,physical_pins=326,fitted_components_top=76,buzzer_circuit_omitted_with_user_authorization=True,source_placement_schematic_pass=True,full_routing_complete=False,native_PCB_DRC_pass=False,carrier_and_fasteners_qualified=False,manufacturing_release=False)
 (OUT/'source-milestone-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
