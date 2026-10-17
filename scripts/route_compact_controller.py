#!/usr/bin/env python3
"""Route a compact native development candidate; independent DRC remains mandatory.

No reference copper is translated into a moved layout. Inner1 is reserved for
GND; all new signal vias retain 0.50/0.30 mm pad/drill. Clock routing stays top.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from shapely.geometry import Point,Polygon,LineString
from shapely.ops import unary_union
from pcb_geometry import Copper,pad_shape,LAYERS
import route_controller_connections as router
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts/compact-controller'
router.STEP=.025;router.LOW=-14;router.N=1121;router.LAYOUT=['top','bottom','inner2']
xy=router.xy;N=router.N

def masks(records,copper,key,widths_by_layer,layers):
 wi=[Image.new('L',(N,N)) for _ in layers];vi=[Image.new('L',(N,N)) for _ in LAYERS]
 wd=[ImageDraw.Draw(i) for i in wi];vd=[ImageDraw.Draw(i) for i in vi]
 def draw(ds,stack,ls,shape,margin):
  for layer in ls:
   if layer not in stack:continue
   polygon=shape.buffer(margin[layer],quad_segs=16)
   for piece in polygon.geoms if hasattr(polygon,'geoms') else [polygon]:
    if piece.geom_type=='Polygon':ds[stack.index(layer)].polygon([xy(x,y) for x,y in piece.exterior.coords],fill=1)
 wm={l:.15+widths_by_layer[l]/2+.012 for l in layers};vm={l:.15+.25+.012 for l in LAYERS}
 for e,k,shapes in copper.elements():
  for l,shape in shapes.items():
   if k!=key:draw(wd,layers,[l],shape,wm)
   if k!=key or e['type'] in ['pcb_smtpad','pcb_plated_hole']:
    draw(vd,LAYERS,[l],shape,{l:.30+.012} if k==key else vm)
 for e in records:
  if e['type']=='pcb_keepout':
   shape=Point(e['center']['x'],e['center']['y']).buffer(e['radius'],quad_segs=64)
   draw(wd,layers,layers,shape,wm);draw(vd,LAYERS,LAYERS,shape,vm)
  elif e['type'] in ['pcb_hole','pcb_plated_hole','pcb_via']:
   h={**e,'shape':'circle' if e['type']!='pcb_plated_hole' else e['shape'],'width':e.get('hole_width',e.get('hole_diameter')),'height':e.get('hole_height',e.get('hole_diameter'))}
   hole=pad_shape(h)
   clearance=.45 if e['type']=='pcb_plated_hole' else .2
   draw(vd,LAYERS,LAYERS,hole,{l:.15+clearance+.012 for l in LAYERS})
   if e['type']=='pcb_hole':draw(wd,layers,layers,hole,{l:.2+widths_by_layer[l]/2+.012 for l in layers})
 # Preserve the crystal top-copper guard and the adjacent inner1 reference.
 # Signal-via antipads must also remain outside that guard. Inner2/bottom
 # signal traces may pass behind the continuous inner1 ground reference.
 if copper.nets[key] not in ['GND','XIN','XOUT','XTAL_OUT']:
  clock=[]
  for e,k,shapes in copper.elements():
   if e['type']=='pcb_trace' and copper.nets.get(k) in ['XIN','XOUT','XTAL_OUT']:
    clock.extend(LineString([(a['x'],a['y']),(b['x'],b['y'])]).buffer(.25) for a,b in zip(e['route'],e['route'][1:]))
  exempt=[]
  for port in copper.ports.values():
   sp=copper.source[port['source_port_id']]
   if copper.names[sp['source_component_id']]=='U_MCU' and sp['pin_number'] in [20,21]:exempt.append(Point(port['x'],port['y']).buffer(.55))
  if clock:
   guard=unary_union(clock).difference(unary_union(exempt))
   draw(wd,layers,['top'],guard,{l:widths_by_layer[l]/2+.012 for l in layers})
   draw(vd,LAYERS,LAYERS,guard,{l:.25+.012 for l in LAYERS})
 for l,d in zip(layers,wd):
  margin=.25+widths_by_layer[l]/2+.012
  edge=math.ceil(margin/router.STEP);far=math.floor((28-margin)/router.STEP)
  d.rectangle([0,0,edge,N-1],fill=1);d.rectangle([far,0,N-1,N-1],fill=1);d.rectangle([0,0,N-1,edge],fill=1);d.rectangle([0,far,N-1,N-1],fill=1)
 for d in vd:
  margin=.25+.25+.012;edge=math.ceil(margin/router.STEP);far=math.floor((28-margin)/router.STEP)
  d.rectangle([0,0,edge,N-1],fill=1);d.rectangle([far,0,N-1,N-1],fill=1);d.rectangle([0,0,N-1,edge],fill=1);d.rectangle([0,far,N-1,N-1],fill=1)
 return [np.asarray(i,dtype=np.bool_) for i in wi],[np.asarray(i,dtype=np.bool_) for i in vi]
router.masks=masks
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--restart',action='store_true');p.add_argument('--net');p.add_argument('--all',action='store_true');p.add_argument('--folder',default='artifacts/compact-controller');args=p.parse_args()
 OUT=ROOT/args.folder
 target=OUT/'routing-construction.circuit.json';source=OUT/'unrouted.circuit.json';history_path=OUT/'routing-construction.json'
 records=json.loads((source if args.restart or not target.exists() else target).read_text())
 history=[] if args.restart or not history_path.exists() else json.loads(history_path.read_text())
 if args.restart or not target.exists():
  ports=[e for e in records if e['type']=='source_port']
  for net in [e for e in records if e['type']=='source_net']:
   records.append({'type':'source_trace','source_trace_id':'source_trace_controller_route_'+net['name'],'connected_source_port_ids':[] if net['name']=='GND' else [e['source_port_id'] for e in ports if e.get('subcircuit_connectivity_map_key')==net['subcircuit_connectivity_map_key']],'connected_source_net_ids':[net['source_net_id']],'subcircuit_connectivity_map_key':net['subcircuit_connectivity_map_key'],'subcircuit_id':net['subcircuit_id']})
 order=['XIN','XOUT','XTAL_OUT','SENSE1','SENSE2','CP1','CP2','VCP','VREG','BUCK_BST','BUCK_SW','A_PLUS','A_MINUS','B_PLUS','B_MINUS','MCU_DP','MCU_DM','USB_DP','USB_DM','PD_VBUS','LOGIC_IN','DATA_VBUS','V1V1']
 if args.all:order+=sorted({e['name'] for e in records if e['type']=='source_net'}-set(order)-{'GND'})
 if args.net:order=[args.net]
 failed=[]
 for name in order:
  for attempt in range(100):
   copper=Copper(records);key=next(k for k,n in copper.nets.items() if n==name)
   members,roots=copper.groups(key);island_count=len({root for (e,_,_),root in zip(members,roots) if e['type'] in ['pcb_smtpad','pcb_plated_hole']})
   proof=None;failures=[]
   for rank in range(min(island_count,16)):
    try:
     proof=router.connect(records,name,attempt,['top'] if name in ['XIN','XOUT','XTAL_OUT'] else None,start_rank=rank)
     break
    except RuntimeError as err:failures.append({'start_rank':rank,'error':str(err)})
   if failures and proof is None:
    failed.append({'net':name,'unrouted_islands':island_count,'start_attempts':failures});print(json.dumps(failed[-1]),flush=True);break
   if proof is None:break
   history.append(proof);target.write_text(json.dumps(records,indent=2)+'\n');history_path.write_text(json.dumps(history,indent=2)+'\n');print(json.dumps(proof),flush=True)
  else:raise RuntimeError(name+': iteration limit')
 target.write_text(json.dumps(records,indent=2)+'\n')
 c=Copper(records);opens=c.connectivity()
 report={'scope':'Native routing construction intermediate; no manufacturing release','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'circuit_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'trace_count':sum(e['type']=='pcb_trace' for e in records),'via_count':sum(e['type']=='pcb_via' for e in records),'failed_construction':failed,'nets_with_opens':len(opens),'opens':opens,'inner1_reserved_for_GND':True,'USB_pair_geometry_and_impedance_qualified':False,'manufacturing_release':False}
 (OUT/'routing-progress.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='opens'}),flush=True)
