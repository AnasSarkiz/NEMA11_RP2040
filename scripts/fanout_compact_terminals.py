#!/usr/bin/env python3
"""Construct explicitly listed 0.45/0.30 mm Type VII capped terminal escapes.

This is a process-dependent construction candidate. Supplier lands are untouched;
full copper, mask, CAM, process and assembly qualification remain mandatory.
"""
import argparse,json,math
from pathlib import Path
from shapely.geometry import Point,LineString
from pcb_geometry import Copper,pad_shape,LAYERS
from compact_via_geometry import via_site_errors
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--folder',required=True);p.add_argument('--part',choices=['U_DRV','U_FLASH'],required=True);args=p.parse_args()
folder=ROOT/args.folder;path=folder/'routing-construction.circuit.json';records=json.loads(path.read_text());c=Copper(records);LAYERS=c.layers
name=args.part;component=next(e for e in records if e['type']=='pcb_component' and c.names[e['source_component_id']]==name)
if name=='U_FLASH':
 ep=next(e for e in records if e.get('pcb_via_id')=='compact_GND_U_FLASH_EP');assert ep['hole_diameter']==.3;ep['outer_diameter']=.5
ports=[e for e in c.ports.values() if c.names[c.source[e['source_port_id']]['source_component_id']]==name and c.source[e['source_port_id']].get('subcircuit_connectivity_map_key') and c.nets[c.source[e['source_port_id']]['subcircuit_connectivity_map_key']]!='GND']
# Preserve the published pin identities and genuinely connected static straps.
def unconstrained_sites(port):
 if name!='U_DRV':return 0
 sp=c.source[port['source_port_id']];key=sp['subcircuit_connectivity_map_key']
 pad=next(e for e in records if e['type']=='pcb_smtpad' and e.get('pcb_port_id')==port['pcb_port_id']);g=pad_shape(pad);b=g.bounds
 dx=g.centroid.x-component['center']['x'];dy=g.centroid.y-component['center']['y'];normal=(math.copysign(1,dx),0) if abs(dx)>abs(dy) else (0,math.copysign(1,dy));half=(b[2]-b[0])/2 if normal[0] else (b[3]-b[1])/2
 count=0
 for sign in [-1,1]:
  x=g.centroid.x+normal[0]*sign*(half+.05);y=g.centroid.y+normal[1]*sign*(half+.05)
  allowed=[e['pcb_smtpad_id'] for e,k,shapes in c.elements() if k==key and e['type']=='pcb_smtpad' and any(Point(x,y).distance(q)<.30 for q in shapes.values())]
  count+=not bool(via_site_errors(records,c,key,x,y,diameter=.45,allowed_pad_ids=allowed))
 return count
ports.sort(key=lambda e:(unconstrained_sites(e),c.source[e['source_port_id']]['pin_number']))
plan=[];failures=[]
def snapshot(records):
 c=Copper(records);elements=c.elements();c.elements=lambda:elements;return c
for port in ports:
 c=snapshot(records);sp=c.source[port['source_port_id']];pin=sp['pin_number'];key=sp['subcircuit_connectivity_map_key'];identifier=f'compact_terminal_{name}_{pin}'
 if any(e.get('pcb_via_id')==identifier for e in records):continue
 pad=next(e for e in records if e['type']=='pcb_smtpad' and e.get('pcb_port_id')==port['pcb_port_id']);shape=pad_shape(pad);b=shape.bounds
 dx=shape.centroid.x-component['center']['x'];dy=shape.centroid.y-component['center']['y'];normal=(math.copysign(1,dx),0) if abs(dx)>abs(dy) else (0,math.copysign(1,dy))
 centre=(shape.centroid.x,shape.centroid.y);half=(b[2]-b[0])/2 if normal[0] else (b[3]-b[1])/2
 if name=='U_DRV':
  direction=-1 if pin%2==0 else 1
  offsets=[direction*(half+.05),-direction*(half+.05),direction*(half+.075),-direction*(half+.075)]
 else:
  # Alternate inside rows on the WSON8's 0.5 mm pitch. Near-row annuli
  # overlap only their own terminal; far-row sites clear the centre EP.
  near=pin in [1,3,5,7];offsets=[-(half+(.175 if near else .54))]
 rejected=[];chosen=None
 for offset in offsets:
  x=centre[0]+normal[0]*offset;y=centre[1]+normal[1]*offset
  # Filled/capped terminal construction may touch another explicitly listed
  # pad of the same net (e.g. its shunt terminal); record every reviewed pad.
  allowed=[e['pcb_smtpad_id'] for e,k,shapes in c.elements() if k==key and e['type']=='pcb_smtpad' and any(Point(x,y).distance(g)<.30 for g in shapes.values())]
  errors=via_site_errors(records,c,key,x,y,diameter=.45,allowed_pad_ids=allowed)
  wire=LineString([(port['x'],port['y']),(x,y)]).buffer(.08,cap_style=1)
  for e,k,shapes in c.elements():
   if k!=key and 'top' in shapes and wire.distance(shapes['top'])<.15-1e-6:errors.append('top stub foreign copper '+e[e['type']+'_id'])
  if not errors:chosen=(x,y,offset);break
  rejected.append({'radial_offset_mm':offset,'errors':sorted(set(errors))})
 if chosen is None:
  failures.append({'part':name,'pin':pin,'net':c.nets[key],'rejected_candidates':rejected});continue
 x,y,offset=chosen;net=next(e for e in records if e['type']=='source_net' and e['subcircuit_connectivity_map_key']==key)
 common=dict(source_net_id=net['source_net_id'],source_trace_id='source_trace_controller_route_'+net['name'],subcircuit_connectivity_map_key=key,subcircuit_id=net['subcircuit_id'])
 records.append(dict(type='pcb_via',pcb_via_id=identifier,x=x,y=y,outer_diameter=.45,hole_diameter=.3,layers=LAYERS,from_layer='top',to_layer='bottom',tented_on_top=True,tented_on_bottom=True,**common))
 records.append(dict(type='pcb_trace',pcb_trace_id=identifier+'_stub',pcb_port_ids=[port['pcb_port_id']],route=[dict(route_type='wire',x=port['x'],y=port['y'],width=.16,layer='top',start_pcb_port_id=port['pcb_port_id']),dict(route_type='wire',x=x,y=y,width=.16,layer='top')],**common))
 overlap=Point(x,y).buffer(.225,quad_segs=64).intersection(shape).area
 plan.append(dict(part=name,pin=pin,net=c.nets[key],via=identifier,owner_pad=pad['pcb_smtpad_id'],reviewed_same_net_pads=allowed,centre_mm=[x,y],radial_offset_mm=offset,annulus_owner_land_overlap_mm2=overlap,requires_Type_VII_filled_capped=overlap>1e-8))
path.write_text(json.dumps(records,indent=2)+'\n')
report=dict(scope='Terminal-via construction candidate; not a manufacturing or complete connectivity certificate',part=name,pad_diameter_mm=.45,drill_diameter_mm=.3,original_supplier_lands_unchanged=True,flash_EP_barrel_pad_mm=.5 if name=='U_FLASH' else None,constructed=plan,failed=failures,manufacturing_release=False)
(folder/('terminal-fanout-'+name+'.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
