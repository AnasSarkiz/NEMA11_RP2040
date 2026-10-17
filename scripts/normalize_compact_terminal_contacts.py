#!/usr/bin/env python3
"""Represent real capped-via/land contacts explicitly for native trace topology.

The independent copper graph recognizes a plated annulus touching an SMD land.
The native trace graph also needs a trace endpoint at that land. Add a nonzero
native trace entirely contained in the unchanged same-net supplier land. This
does not enlarge copper, move a land, or bypass a physical connectivity check.
"""
import argparse,hashlib,json,math
from pathlib import Path
from shapely.geometry import LineString
from pcb_geometry import Copper,pad_shape

p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--additional-ports',default='');a=p.parse_args()
data=a.input.read_bytes();records=json.loads(data);c=Copper(records);added=[]
targets=[]
for via in [e for e in records if e['type']=='pcb_via' and e['pcb_via_id'].startswith('compact_terminal_')]:
    port=next((port for port in c.ports.values() if math.dist((port['x'],port['y']),(via['x'],via['y']))<1e-7 and c.source[port['source_port_id']].get('subcircuit_connectivity_map_key')==c.key(via)),None)
    if port is not None:targets.append((via['pcb_via_id']+'_land_contact',port,via['pcb_via_id']))
for qualified in filter(None,a.additional_ports.split(',')):
    part,pin=qualified.rsplit('.',1)
    port=next(port for port in c.ports.values() if c.names[c.source[port['source_port_id']]['source_component_id']]==part and str(c.source[port['source_port_id']]['pin_number'])==pin)
    targets.append(('compact_existing_land_'+part+'_'+pin,port,None))
for identifier,port,via_id in targets:
    if any(e.get('pcb_trace_id')==identifier for e in records):continue
    pad=next(e for e in records if e['type']=='pcb_smtpad' and e.get('pcb_port_id')==port['pcb_port_id'])
    shape=pad_shape(pad);x,y=port['x'],port['y'];end=None;key=c.key(pad)
    net=next(e for e in records if e['type']=='source_net' and e['subcircuit_connectivity_map_key']==key)
    for dx,dy in [(.01,0),(-.01,0),(0,.01),(0,-.01)]:
        wire=LineString([(x,y),(x+dx,y+dy)]).buffer(.08,quad_segs=64)
        if shape.covers(wire):end=(x+dx,y+dy);break
    if end is None:raise ValueError('Cannot represent contact within original land: '+identifier)
    branch=next(e for e in records if e['type']=='source_trace' and e.get('connected_source_port_ids')==[port['source_port_id']])
    records.append(dict(type='pcb_trace',pcb_trace_id=identifier,pcb_port_ids=[port['pcb_port_id']],source_trace_id=branch['source_trace_id'],source_net_id=net['source_net_id'],subcircuit_id=net['subcircuit_id'],subcircuit_connectivity_map_key=key,route=[dict(route_type='wire',x=x,y=y,width=.16,layer=pad['layer'],start_pcb_port_id=port['pcb_port_id']),dict(route_type='wire',x=end[0],y=end[1],width=.16,layer=pad['layer'],end_pcb_port_id=port['pcb_port_id'])]))
    added.append(dict(trace=identifier,land=pad['pcb_smtpad_id'],via=via_id,added_copper_outside_original_land_mm2=0))
output=(json.dumps(records,indent=2)+'\n').encode();a.input.write_bytes(output)
report=dict(scope='Explicit native topology for existing capped terminal contacts; supplier copper unchanged',input_sha256=hashlib.sha256(data).hexdigest(),circuit_sha256=hashlib.sha256(output).hexdigest(),contacts=added,all_added_trace_geometry_contained_in_original_same_net_supplier_lands=True,manufacturing_release=False)
(a.input.parent/'terminal-contact-construction.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(explicit_land_contacts=len(added),copper_geometry_enlarged=False)))
