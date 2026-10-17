#!/usr/bin/env python3
"""Construct real exposed-pad and local clock ground barrels; no via-size reduction."""
import argparse,json,math
from pathlib import Path
from shapely.geometry import Point,LineString
from shapely.strtree import STRtree
from pcb_geometry import Copper,pad_shape,LAYERS
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--folder',default='artifacts/compact-routing');args=p.parse_args();folder=ROOT/args.folder;path=folder/'routing-construction.circuit.json';records=json.loads(path.read_text());results=[]
c=Copper(records);net=next(e for e in records if e['type']=='source_net' and e['name']=='GND');key=net['subcircuit_connectivity_map_key'];common=dict(source_net_id=net['source_net_id'],source_trace_id='source_trace_controller_route_GND',subcircuit_connectivity_map_key=key,subcircuit_id=net['subcircuit_id'])
geometry_cache={}
def geometry():
 if geometry_cache.get('length')!=len(records):
  elements=Copper(records).elements();geometry_cache.update(length=len(records),elements=elements,flat=[(e,k,s) for e,k,ss in elements for s in ss.values()])
  geometry_cache['tree']=STRtree([s for e,k,s in geometry_cache['flat']])
 return geometry_cache['flat'],geometry_cache['tree']
def legal(x,y,diameter=.5,thermal=False):
 shape=Point(x,y).buffer(diameter/2,quad_segs=32)
 if min(x+14,14-x,y+14,14-y)<.25+diameter/2:return False
 flat,tree=geometry()
 for index in tree.query(shape.buffer(.151)):
  e,k,s=flat[index]
  if k!=key and shape.distance(s)<.15+1e-6:return False
  if not thermal and e['type'] in ['pcb_smtpad','pcb_plated_hole'] and shape.distance(s)<.05+1e-6:return False
 for e in records:
  if e['type']=='pcb_keepout' and math.dist((x,y),(e['center']['x'],e['center']['y']))<e['radius']+diameter/2+.005:return False
  if e['type'] in ['pcb_hole','pcb_via','pcb_plated_hole']:
   h={**e,'shape':'circle' if e['type']!='pcb_plated_hole' else e['shape'],'width':e.get('hole_width',e.get('hole_diameter')),'height':e.get('hole_height',e.get('hole_diameter'))}
   drill=pad_shape(h);required=.45 if e['type']=='pcb_plated_hole' else .2
   if Point(x,y).buffer(.15).distance(drill)<required+1e-6:return False
 return True

def barrel(x,y,label,thermal=False):
 identifier='compact_GND_'+label
 records.append(dict(type='pcb_via',pcb_via_id=identifier,x=x,y=y,outer_diameter=.6 if thermal else .5,hole_diameter=.3,layers=LAYERS,from_layer='top',to_layer='bottom',tented_on_top=not thermal,tented_on_bottom=True,**common));return identifier
for name,pin in [('U_MCU',57),('U_DRV',29),('U_FLASH',9)]:
 if any(e.get('pcb_via_id')=='compact_GND_'+name+'_EP' for e in records):continue
 port=next(p for p in c.ports.values() if c.names[c.source[p['source_port_id']]['source_component_id']]==name and c.source[p['source_port_id']]['pin_number']==pin)
 assert legal(port['x'],port['y'],.6,True),'No legal reviewed thermal barrel: '+name
 via=barrel(port['x'],port['y'],name+'_EP',True);results.append(dict(pin=name+'.'+str(pin),via=via,requires_Type_VII_filled_capped=True))
for name,pin in [('Y_MCU',2),('Y_MCU',4),('C_XIN',2),('C_XOUT',2)]:
 label=name+'_'+str(pin)
 if any(e.get('pcb_via_id')=='compact_GND_'+label for e in records):continue
 c=Copper(records);port=next(p for p in c.ports.values() if c.names[c.source[p['source_port_id']]['source_component_id']]==name and c.source[p['source_port_id']]['pin_number']==pin)
 found=None
 candidates=[]
 for radius in [r/40 for r in range(24,49)]:
  for angle in range(0,360,5):
   x=round((port['x']+radius*math.cos(math.radians(angle)))*40)/40;y=round((port['y']+radius*math.sin(math.radians(angle)))*40)/40
   candidates.append((math.dist((x,y),(port['x'],port['y'])),x,y))
 for distance,x,y in sorted(candidates):
  if distance>1.2 or not legal(x,y):continue
  shape=LineString([(port['x'],port['y']),(x,y)]).buffer(.08,quad_segs=16)
  if any(k!=key and 'top' in shapes and shape.distance(shapes['top'])<.15+1e-6 for e,k,shapes in c.elements()):continue
  found=(x,y,distance);break
 if not found:results.append(dict(pin=name+'.'+str(pin),error='No legal direct local ground stitch'));continue
 x,y,d=found;via=barrel(x,y,label)
 records.append(dict(type='pcb_trace',pcb_trace_id='compact_GND_trace_'+label,pcb_port_ids=[port['pcb_port_id']],route=[dict(route_type='wire',x=port['x'],y=port['y'],width=.16,layer='top',start_pcb_port_id=port['pcb_port_id']),dict(route_type='wire',x=x,y=y,width=.16,layer='top')],**common));results.append(dict(pin=name+'.'+str(pin),via=via,ground_return_distance_mm=d))
path.write_text(json.dumps(records,indent=2)+'\n');(folder/'clock-ground-construction.json').write_text(json.dumps(dict(scope='Constructed physical clock returns and three reviewed exposed-pad barrels; final copper/plane check required',results=results,manufacturing_release=False),indent=2)+'\n');print(json.dumps(results));raise SystemExit(any('error' in r for r in results))
