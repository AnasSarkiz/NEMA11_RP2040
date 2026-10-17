#!/usr/bin/env python3
"""Construct selectively checked capped-via escapes on existing passive lands.

Original supplier copper, paste and mask are retained. New vias are tented on
both sides; existing terminal mask apertures expose only their original lands.
Requires factory acceptance of the selected filled/copper-capped process.
"""
import argparse,json,math
from pathlib import Path
from shapely.geometry import Point,LineString,Polygon
from pcb_geometry import Copper,pad_shape,LAYERS
from compact_via_geometry import via_site_errors,top_stub_errors
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--folder',required=True);p.add_argument('--only',default='');p.add_argument('--via-plan');args=p.parse_args();folder=ROOT/args.folder;path=folder/'routing-construction.circuit.json';records=json.loads(path.read_text());c=Copper(records);LAYERS=c.layers
requested=set(args.only.split(',')) if args.only else set();via_plan=json.loads(Path(args.via_plan).read_text()) if args.via_plan else {}
ports=[e for e in c.ports.values() if c.source[e['source_port_id']].get('subcircuit_connectivity_map_key') and c.nets.get(c.source[e['source_port_id']]['subcircuit_connectivity_map_key']) not in ['XIN','XOUT','XTAL_OUT','MCU_DM','MCU_DP'] and (c.names[c.source[e['source_port_id']]['source_component_id']] not in ['U_MCU','U_DRV','U_FLASH','J_PD','J_DATA','J_MOTOR','Y_MCU'] or c.names[c.source[e['source_port_id']]['source_component_id']]+'.'+str(c.source[e['source_port_id']]['pin_number']) in requested)]
if requested:ports=[e for e in ports if c.names[c.source[e['source_port_id']]['source_component_id']]+'.'+str(c.source[e['source_port_id']]['pin_number']) in requested]
results=[];failed=[]
def snapshot(records):
 c=Copper(records);elements=c.elements();c.elements=lambda:elements;return c
for port in ports:
 c=snapshot(records);sp=c.source[port['source_port_id']];key=sp['subcircuit_connectivity_map_key'];name=c.names[sp['source_component_id']];pin=sp['pin_number'];identifier=f'compact_terminal_{name}_{pin}'
 members,roots=c.groups(key);root=next(r for (e,_,_),r in zip(members,roots) if e.get('pcb_port_id')==port['pcb_port_id'])
 if any(e['type'] in ['pcb_via','pcb_plated_hole'] and r==root for (e,_,_),r in zip(members,roots)):continue
 pad=next(e for e in records if e['type']=='pcb_smtpad' and e.get('pcb_port_id')==port['pcb_port_id']);g=pad_shape(pad);b=g.bounds;layer=pad['layer'];centre=(g.centroid.x,g.centroid.y)
 direction=(1,0) if b[2]-b[0]>=b[3]-b[1] else (0,1);half=(b[2]-b[0])/2 if direction[0] else (b[3]-b[1])/2
 offsets=[0,.1,-.1,.2,-.2,.3,-.3]+[v for gap in [.05,.1,.175,.2,.25,.3] for v in [half+gap,-half-gap]]
 chosen=None;rejections=[]
 sites=[(centre[0]+direction[0]*offset,centre[1]+direction[1]*offset,offset) for offset in offsets]
 if name+'.'+str(pin) in via_plan:sites=[(*via_plan[name+'.'+str(pin)],None)]
 for x,y,offset in sites:
  allowed=[e['pcb_smtpad_id'] for e,k,ss in c.elements() if k==key and e['type']=='pcb_smtpad' and any(Point(x,y).distance(q)<.3 for q in ss.values())]
  errors=via_site_errors(records,c,key,x,y,diameter=.45,allowed_pad_ids=allowed)
  wire=LineString([(port['x'],port['y']),(x,y)]).buffer(.0801,quad_segs=64)
  # A zero-length stub still has a via-to-land physical contact and is recorded
  # without adding a degenerate trace record.
  if math.dist((port['x'],port['y']),(x,y))>.0001:
   if layer=='top':errors.extend(top_stub_errors(records,c,key,[(port['x'],port['y']),(x,y)]))
   for e,k,ss in c.elements():
    if k!=key and layer in ss and wire.distance(ss[layer])<.15:errors.append('foreign stub copper '+e[e['type']+'_id'])
   board=next(e for e in records if e['type']=='pcb_board');outline=Polygon([(v['x'],v['y']) for v in board['outline']])
   if not outline.covers(wire) or wire.distance(outline.boundary)<.25:errors.append('stub board edge')
   for e in records:
    if e['type']=='pcb_keepout' and wire.intersects(Point(e['center']['x'],e['center']['y']).buffer(e['radius'],quad_segs=64)):errors.append('stub mount keepout')
  if not errors:chosen=(x,y,allowed);break
  rejections.append(dict(offset_mm=offset,errors=sorted(set(errors))))
 if chosen is None:
  failed.append(dict(part=name,pin=pin,net=c.nets[key],rejected_candidates=rejections));continue
 x,y,allowed=chosen;net=next(e for e in records if e['type']=='source_net' and e['subcircuit_connectivity_map_key']==key)
 branch=next(e['source_trace_id'] for e in records if e['type']=='source_trace' and e.get('subcircuit_connectivity_map_key')==key and sp['source_port_id'] in e.get('connected_source_port_ids',[]))
 common=dict(source_net_id=net['source_net_id'],source_trace_id=branch,subcircuit_connectivity_map_key=key,subcircuit_id=net['subcircuit_id'])
 records.append(dict(type='pcb_via',pcb_via_id=identifier,x=x,y=y,outer_diameter=.45,hole_diameter=.3,layers=LAYERS,from_layer='top',to_layer='bottom',tented_on_top=True,tented_on_bottom=True,**common))
 if math.dist((port['x'],port['y']),(x,y))>.0001:
  records.append(dict(type='pcb_trace',pcb_trace_id=identifier+'_stub',pcb_port_ids=[port['pcb_port_id']],route=[dict(route_type='wire',x=port['x'],y=port['y'],width=.16,layer=layer,start_pcb_port_id=port['pcb_port_id']),dict(route_type='wire',x=x,y=y,width=.16,layer=layer)],**common))
 results.append(dict(part=name,pin=pin,net=c.nets[key],via=identifier,centre_mm=[x,y],owner_pad=pad['pcb_smtpad_id'],reviewed_same_net_pads=allowed,requires_Type_VII_filled_capped=True,original_land_mask_and_paste_apertures_retained=True))
 path.write_text(json.dumps(records,indent=2)+'\n')
(folder/('passive-terminal-repair.json' if requested else 'passive-terminal-construction.json')).write_text(json.dumps(dict(scope='Capped terminal-via construction; no fabrication or full-routing claim',constructed=results,failed=failed,manufacturing_release=False),indent=2)+'\n')
print(json.dumps(dict(constructed=len(results),failed=[dict(part=v['part'],pin=v['pin'],net=v['net']) for v in failed])))
