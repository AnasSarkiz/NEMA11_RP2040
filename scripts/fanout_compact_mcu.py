#!/usr/bin/env python3
"""Construct ordinary plated RP2040 fanouts before long interconnect routing.

Uses top traces and 0.50/0.30 mm through vias, including legal non-pad spaces
under the package. No blind/micro vias or ordinary via-in-pad are permitted.
"""
import argparse,json,math
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt
from pcb_geometry import Copper
from fast_grid_router import route as fast_route
import route_compact_controller # Configures the compact grid and physical masks.
import route_controller_connections as router
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--folder',default='artifacts/compact-routing');p.add_argument('--restart',action='store_true');args=p.parse_args();folder=ROOT/args.folder;path=folder/'routing-construction.circuit.json';records=json.loads(path.read_text())
if args.restart:
 c=Copper(records)
 records=[e for e in records if e['type'] not in ['pcb_trace','pcb_via','pcb_copper_pour'] or (e['type'] in ['pcb_trace','pcb_via'] and (c.nets.get(c.key(e)) in ['XIN','XOUT','XTAL_OUT'] or e.get('pcb_trace_id','').startswith('compact_GND_') or e.get('pcb_via_id','').startswith('compact_GND_')))]
 c=Copper(records)
 ports=[v for v in c.ports.values() if c.names[c.source[v['source_port_id']]['source_component_id']]=='U_MCU' and c.nets.get(c.source[v['source_port_id']].get('subcircuit_connectivity_map_key')) not in [None,'GND','XIN','XOUT','XTAL_OUT']]
 pc=next(e for e in records if e['type']=='pcb_component' and c.names[e['source_component_id']]=='U_MCU')
 def priority(v):
  dx=v['x']-pc['center']['x'];dy=v['y']-pc['center']['y'];pin=c.source[v['source_port_id']]['pin_number']
  edge=0 if dy>3 else 1 if dx<-3 else 2 if dy<-3 else 3
  return edge,pin%2,pin
 ports.sort(key=priority)
 report=[];N=router.N
 for pp in ports:
  c=Copper(records);sp=c.source[pp['source_port_id']];pin=sp['pin_number'];key=sp['subcircuit_connectivity_map_key'];net=next(e for e in records if e['type']=='source_net' and e['subcircuit_connectivity_map_key']==key);name=net['name'];identifier='compact_MCU_fanout_'+str(pin)
  if any(e.get('pcb_trace_id')==identifier for e in records):continue
  layers=['top'];wire,vias=router.masks(records,c,key,{'top':.16},layers)
  # The via barrel crosses every copper layer; all masks must be clear.
  allowed=np.logical_not(np.logical_or.reduce(vias)) & np.logical_not(wire[0])
  gx,gy=router.xy(pp['x'],pp['y']);goals=[]
  for y in range(max(0,gy-92),min(N,gy+93)):
   for x in range(max(0,gx-92),min(N,gx+93)):
    if (x-gx)**2+(y-gy)**2<=92**2 and allowed[y,x]:goals.append((x,y,0))
  existing={router.xy(e['x'],e['y']):e for e in records if e['type']=='pcb_via' and c.key(e)==key}
  for (x,y),via in existing.items():
   if (x-gx)**2+(y-gy)**2<=92**2 and not wire[0][y,x]:goals.append((x,y,0))
  members,roots=c.groups(key);root=next(r for (e,_,_),r in zip(members,roots) if e.get('pcb_port_id')==pp['pcb_port_id'])
  if any(e['type']=='pcb_via' and r==root for (e,_,_),r in zip(members,roots)):
   report.append(dict(pin=pin,net=name,already_connected_to_same_net_via=True));continue
  starts=router.sample_members(members,root,roots,layers,c.ports);starts={a:b for a,b in starts.items() if 0<=a[0]<N and 0<=a[1]<N and not wire[a[2]][a[1],a[0]]}
  if not goals or not starts:report.append(dict(pin=pin,net=name,error='No legal fanout start/via sites'));continue
  mask=np.ones((N,N),dtype=np.bool_)
  for x,y,z in goals:mask[y,x]=False
  distance=distance_transform_edt(mask);result,expanded=fast_route(wire,np.zeros((1,N,N),dtype=np.uint8),vias,existing,distance,list(starts),goals,1.2,0,False,layers,limit=1500000)
  if result is None:report.append(dict(pin=pin,net=name,error='No legal top fanout route',expanded=expanded));continue
  slim=[result[0]]
  for i in range(1,len(result)-1):
   a,b,d=result[i-1:i+2]
   if (b[0]-a[0],b[1]-a[1])!=(d[0]-b[0],d[1]-b[1]):slim.append(b)
  slim.append(result[-1]);x,y=router.world(result[-1]);old=existing.get(result[-1][:2])
  if old:x,y=old['x'],old['y']
  common=dict(source_net_id=net['source_net_id'],source_trace_id='source_trace_controller_route_'+name,subcircuit_connectivity_map_key=key,subcircuit_id=net['subcircuit_id'])
  route=[dict(route_type='wire',x=router.world(v)[0],y=router.world(v)[1],width=.16,layer='top') for v in slim]
  route[0].update(zip(['x','y'],starts[result[0]]));route[-1].update(x=x,y=y);route[0]['start_pcb_port_id']=pp['pcb_port_id']
  records.append(dict(type='pcb_trace',pcb_trace_id=identifier,pcb_port_ids=[pp['pcb_port_id']],route=route,**common))
  if not old:records.append(dict(type='pcb_via',pcb_via_id=identifier+'_via',x=x,y=y,outer_diameter=.5,hole_diameter=.3,layers=['top','inner1','inner2','bottom'],from_layer='top',to_layer='bottom',tented_on_top=True,tented_on_bottom=True,**common))
  proof=dict(pin=pin,net=name,via_x=x,via_y=y,expanded=expanded,reused_same_net_barrel=bool(old));report.append(proof);print(json.dumps(proof),flush=True)
  path.write_text(json.dumps(records,indent=2)+'\n')
 (folder/'MCU-fanout-construction.json').write_text(json.dumps(dict(scope='Constructed RP2040 top-to-through-via escapes; final copper and connectivity check mandatory',pins=report,failed=[r for r in report if 'error' in r],manufacturing_release=False),indent=2)+'\n')
 path.write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(dict(MCU_fanouts=len(report),failures=[r for r in report if 'error' in r])),flush=True)
else:raise SystemExit('Use --restart to construct fanouts from reserved clock and ground copper')
