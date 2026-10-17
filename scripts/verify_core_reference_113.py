#!/usr/bin/env python3
"""Compare the implemented MCU's physical pins/values to the exact v1.13 source."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
reference=Path(sys.argv[1] if len(sys.argv)>1 else '/workspace/reference-materials/nema14-registry-1.13/artifacts/board.circuit.json')
core=ROOT/'artifacts/rp2040-core/core.circuit.json'

def inventory(records):
    components={e['source_component_id']:e for e in records if e['type']=='source_component'}
    nets={e['subcircuit_connectivity_map_key']:e['name'] for e in records if e['type']=='source_net'}
    ports={(components[e['source_component_id']]['name'],e['pin_number']):nets.get(e.get('subcircuit_connectivity_map_key'))
           for e in records if e['type']=='source_port'}
    return {e['name']:e for e in components.values()},ports
ca,cp=inventory(json.loads(core.read_text()));ra,rp=inventory(json.loads(reference.read_text()));errors=[]
for pin,net in cp.items():
    if pin not in rp or rp[pin]!=net:errors.append({'pin':pin,'core':net,'reference':rp.get(pin)})
for name,c in ca.items():
    r=ra.get(name)
    if r is None:errors.append({'missing_reference_component':name});continue
    for field in ['manufacturer_part_number','resistance','capacitance','frequency']:
        if c.get(field)!=r.get(field):errors.append({'component':name,'field':field,'core':c.get(field),'reference':r.get(field)})
report={'scope':'Implemented MCU subset physical pin/value parity against downloaded exact published v1.13.0',
        'ports_compared':len(cp),'components_compared':len(ca),'errors':errors,
        'core_sha256':hashlib.sha256(core.read_bytes()).hexdigest(),'reference_board_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
        'whole_controller_parity_verified':False,'manufacturing_release':False}
(ROOT/'artifacts/requirements/core-reference-1.13-parity.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'ports_compared':len(cp),'components_compared':len(ca),'errors':errors}))
raise SystemExit(bool(errors))
