#!/usr/bin/env python3
"""Construct missing native copper paths; independent audits remain authoritative."""
import argparse
import json
import math
from pathlib import Path
from collections import defaultdict
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
from shapely.geometry import Point, LineString, Polygon, box
from shapely.ops import unary_union
from pcb_geometry import Copper, pad_shape, LAYERS
from fast_grid_router import route as fast_route

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/controller-pcb'
STEP=.025
LOW=-17.5
N=1601
LAYOUT=['top','bottom','inner2','inner1']
xy=lambda x,y:(round((x-LOW)/STEP),round((y-LOW)/STEP))
world=lambda p:(LOW+p[0]*STEP,LOW+p[1]*STEP)
PHASE={'A_PLUS','A_MINUS','B_PLUS','B_MINUS'}
SENSE={'SENSE1','SENSE2'}


def widths(name):
    # The selected manufacturing stack requires 1 oz finished inner copper.
    # At 0.67 A the nominal 30 C IPC-2221 screen is 0.231 mm internally.
    if name in PHASE:return {l:.30 for l in LAYOUT}
    if name in SENSE:return {l:.30 for l in LAYOUT}
    if name in ['PD_VBUS','LOGIC_IN','DATA_VBUS']:return {l:.30 for l in LAYOUT}
    return {l:.16 for l in LAYOUT}


def masks(records, copper, key, widths_by_layer, layers):
    wire_images=[Image.new('L',(N,N)) for _ in layers]
    via_images=[Image.new('L',(N,N)) for _ in LAYERS]
    wire_draws=[ImageDraw.Draw(i) for i in wire_images]
    via_draws=[ImageDraw.Draw(i) for i in via_images]
    def draw(ds, stack, ls, geometry, margins):
        for layer in ls:
            if layer not in stack:continue
            expanded=geometry.buffer(margins[layer],quad_segs=16)
            pieces=list(expanded.geoms) if hasattr(expanded,'geoms') else [expanded]
            for p in pieces:
                if p.geom_type=='Polygon':ds[stack.index(layer)].polygon([xy(x,y) for x,y in p.exterior.coords],fill=1)
    wm={l:.15+widths_by_layer[l]/2+.018 for l in layers}
    vm={l:.15+.25+.018 for l in LAYERS}
    for e,k,shapes in copper.elements():
        for layer,shape in shapes.items():
            if k != key:draw(wire_draws,layers,[layer],shape,wm)
            # New vias cannot occupy any component pad, including same-net pads.
            # Existing same-net barrels are explicit reusable transitions below.
            if k != key or e['type'] in ['pcb_smtpad','pcb_plated_hole']:
                # Same-net adjacent vias retain >=0.10 mm mask web between
                # a 0.30 mm drill and a pad opening expanded by 0.05 mm.
                margin={l:.30+.018 for l in LAYERS} if k==key else vm
                draw(via_draws,LAYERS,[layer],shape,margin)
    clock=[]
    names=copper.names
    for e in records:
        if e['type']=='pcb_keepout':
            c=e['center'];r=e['radius']
            # Conservative square also clears this native checker's envelope.
            shape=Point(c['x'],c['y']).buffer(r+.005,quad_segs=64) if copper.nets[key]=='STATUS_B_K' else box(c['x']-r,c['y']-r,c['x']+r,c['y']+r)
            draw(wire_draws,layers,layers,shape,wm);draw(via_draws,LAYERS,LAYERS,shape,vm)
        elif e['type'] in ['pcb_hole','pcb_plated_hole','pcb_via']:
            h={**e,'shape':'circle' if e['type']!='pcb_plated_hole' else e['shape'],
               'width':e.get('hole_width',e.get('hole_diameter')),'height':e.get('hole_height',e.get('hole_diameter'))}
            hole=pad_shape(h)
            draw(via_draws,LAYERS,LAYERS,hole,{l:.15+.20+.018 for l in LAYERS})
            if e['type']=='pcb_hole':draw(wire_draws,layers,layers,hole,{l:.2+widths_by_layer[l]/2+.018 for l in layers})
        elif e['type']=='pcb_courtyard_outline':
            component=next(p for p in records if p['type']=='pcb_component' and p['pcb_component_id']==e['pcb_component_id'])
            if names[component['source_component_id']]=='Y_MCU':clock.append(Polygon([(p['x'],p['y']) for p in e['outline']]))
    for e,k,shapes in copper.elements():
        if copper.nets.get(k) in ['XIN','XOUT','XTAL_OUT']:
            clock.extend(shapes.values())
    if clock:
        protected=unary_union(clock).buffer(.15)
        draw(wire_draws,layers,layers,protected,wm)
        draw(via_draws,LAYERS,LAYERS,protected,vm)
    usb=json.loads((ROOT/'config/controller-usb-reference.json').read_text())
    for core in usb['cores']:
        guard=LineString(core['centerline']).buffer(usb['reference_construction_buffer_mm'])
        draw(wire_draws,layers,[core['reference_layer']],guard,wm)
        draw(via_draws,LAYERS,LAYERS,guard,vm)
        if copper.nets[key] in PHASE:
            trunk=LineString(core['centerline']).buffer(usb['motor_to_USB_trunk_buffer_mm'])
            draw(wire_draws,layers,[core['layer']],trunk,wm)
    # The board is asymmetric: X +/-17.5, Y -17.5..22.5 mm.
    for layer,d in zip(layers,wire_draws):
        margin=.25+widths_by_layer[layer]/2+.018
        left=math.ceil(margin/STEP);right=math.floor((35-margin)/STEP)
        bottom=math.ceil(margin/STEP);top=math.floor((40-margin)/STEP)
        d.rectangle([0,0,left,N-1],fill=1);d.rectangle([right,0,N-1,N-1],fill=1)
        d.rectangle([0,0,N-1,bottom],fill=1);d.rectangle([0,top,N-1,N-1],fill=1)
    if copper.nets[key] in PHASE and 'inner1' in layers:
        # The corrected USB locator blocks inherited phase copper. Permit a
        # bounded repair on inner1 only in the driver area, far from the MCU
        # USB/clock reference. Final plane coverage is checked independently.
        d=wire_draws[layers.index('inner1')]
        left,bottom=xy(-4,-17.1);right,top=xy(9,-8.5)
        d.rectangle([0,0,left,N-1],fill=1);d.rectangle([right,0,N-1,N-1],fill=1)
        d.rectangle([0,0,N-1,bottom],fill=1);d.rectangle([0,top,N-1,N-1],fill=1)
    for d in via_draws:
        margin=.25+.25+.018
        left=math.ceil(margin/STEP);right=math.floor((35-margin)/STEP)
        bottom=math.ceil(margin/STEP);top=math.floor((40-margin)/STEP)
        d.rectangle([0,0,left,N-1],fill=1);d.rectangle([right,0,N-1,N-1],fill=1)
        d.rectangle([0,0,N-1,bottom],fill=1);d.rectangle([0,top,N-1,N-1],fill=1)
    wire=[np.asarray(i,dtype=np.bool_) for i in wire_images]
    return wire,[np.asarray(i,dtype=np.bool_) for i in via_images]


def sample_members(members, root, roots, layers, ports):
    points={}
    def add(x,y,l):
        if l in layers:points[(*xy(x,y),layers.index(l))]=(x,y)
    for (e,_,shapes),r in zip(members,roots):
        if r!=root:continue
        if e['type'] in ['pcb_smtpad','pcb_plated_hole']:
            for l,shape in shapes.items():
                if l not in layers:continue
                x0,y0,x1,y1=shape.bounds
                for x in np.arange(x0+.03,x1,.075):
                    for y in np.arange(y0+.03,y1,.075):
                        if shape.buffer(-.003).covers(Point(x,y)):add(x,y,l)
                p=ports[e['pcb_port_id']]
                if e['type']=='pcb_smtpad':add(p['x'],p['y'],l)
        elif e['type']=='pcb_via':
            for l in e['layers']:
                add(e['x'],e['y'],l)
                radius=(e['outer_diameter']+e['hole_diameter'])/4
                for angle in range(0,360,30):
                    add(e['x']+radius*math.cos(math.radians(angle)),e['y']+radius*math.sin(math.radians(angle)),l)
        elif e['type']=='pcb_trace':
            a,b=e['route'];distance=math.hypot(a['x']-b['x'],a['y']-b['y']);count=max(1,math.ceil(distance/.10))
            for k in range(count+1):add(a['x']+(b['x']-a['x'])*k/count,a['y']+(b['y']-a['y'])*k/count,a['layer'])
    return points


def connect(records, name, attempt, layer_override=None, start_rank=0):
    copper=Copper(records)
    net=next(e for e in records if e['type']=='source_net' and e['name']==name)
    key=net['subcircuit_connectivity_map_key']
    members,roots=copper.groups(key)
    islands=defaultdict(list)
    for (e,_,_),r in zip(members,roots):
        if e['type'] in ['pcb_smtpad','pcb_plated_hole']:islands[r].append(e)
    if len(islands)<2:return None
    def choice(root):
        parts={copper.names[copper.source[copper.ports[e['pcb_port_id']]['source_port_id']]['source_component_id']] for e in islands[root]}
        return (0 if parts=={'J_MOTOR'} else 1,len(islands[root]),root)
    startroot=sorted(islands,key=choice)[start_rank % len(islands)]
    layers=layer_override or (['top','bottom'] if name=='PD_VBUS' else ['top','bottom','inner2'] if name=='LOGIC_IN' else LAYOUT)
    w=widths(name)
    wire,vias=masks(records,copper,key,w,layers)
    def width_at(node):
        return w[layers[node[2]]]
    starts=sample_members(members,startroot,roots,layers,copper.ports)
    goals={}
    for root in islands:
        if root!=startroot:goals.update(sample_members(members,root,roots,layers,copper.ports))
    legal=lambda q:0<=q[0]<N and 0<=q[1]<N and not wire[q[2]][q[1],q[0]]
    starts={q:p for q,p in starts.items() if legal(q)}
    goals={q:p for q,p in goals.items() if legal(q)}
    if not starts or not goals:raise RuntimeError(f'{name}: no legal start/target cells ({len(starts)}/{len(goals)})')
    mask=np.ones((N,N),dtype=np.bool_)
    for x,y,z in goals:mask[y,x]=False
    distance=distance_transform_edt(mask)
    existing={xy(e['x'],e['y']):e for e in records if e['type']=='pcb_via' and copper.key(e)==key}
    soft=np.zeros((len(layers),N,N),dtype=np.uint8)
    if 'inner2' in layers:soft[layers.index('inner2')]=1
    path,expanded=fast_route(wire,soft,vias,existing,distance,list(starts),list(goals),1.7,.12,name in PHASE,layers,limit=8000000,inner_cost=6)
    if path is None:raise RuntimeError(f'{name}: no legal grid route ({expanded} expansions)')
    slim=[path[0]]
    for i in range(1,len(path)-1):
        a,b,c=path[i-1:i+2]
        if tuple(b[k]-a[k] for k in range(3))!=tuple(c[k]-b[k] for k in range(3)) or width_at(a)!=width_at(b) or width_at(b)!=width_at(c):slim.append(b)
    slim.append(path[-1])
    uid=f'controller_connection_{name}_{attempt}'
    while any(e.get('pcb_trace_id','').startswith(uid) for e in records):uid+='_next'
    source_trace='source_trace_controller_route_'+name
    common={'source_net_id':net['source_net_id'],'source_trace_id':source_trace,
            'subcircuit_connectivity_map_key':key,'subcircuit_id':net['subcircuit_id']}
    route=[];added=[]
    for i,node in enumerate(slim):
        x,y=world(node)
        old=existing.get((node[0],node[1]))
        if old:x,y=old['x'],old['y']
        layer=layers[node[2]]
        if i and node[2]!=slim[i-1][2]:
            diameter=old['outer_diameter'] if old else .50
            drill=old['hole_diameter'] if old else .30
            route.append({'route_type':'via','x':x,'y':y,'from_layer':layers[slim[i-1][2]],'to_layer':layer,
                          'via_diameter':diameter,'via_hole_diameter':drill})
            if not old:
                added.append({'type':'pcb_via','pcb_via_id':uid+f'_via_{i}','x':x,'y':y,
                              'outer_diameter':.50,'hole_diameter':.30,'layers':LAYERS,
                              'from_layer':'top','to_layer':'bottom','tented_on_top':True,'tented_on_bottom':True,**common})
        route.append({'route_type':'wire','x':x,'y':y,'layer':layer,'width':width_at(node)})
    route[0].update(zip(['x','y'],starts[path[0]]));route[-1].update(zip(['x','y'],goals[path[-1]]))
    port_ids=[]
    for point,field in [(route[0],'start_pcb_port_id'),(route[-1],'end_pcb_port_id')]:
        for e in records:
            if e['type'] in ['pcb_smtpad','pcb_plated_hole'] and copper.key(e)==key and point['layer'] in e.get('layers',[e.get('layer')]) and pad_shape(e).buffer(.001).covers(Point(point['x'],point['y'])):
                point[field]=e['pcb_port_id'];port_ids.append(e['pcb_port_id']);break
    before=len(records)
    records.extend(added)
    sections=[]
    for a,b in zip(route,route[1:]):
        if a['route_type']!='wire' or b['route_type']!='wire' or a['layer']!=b['layer']:continue
        width=min(a['width'],b['width']);aa={**a,'width':width};bb={**b,'width':width}
        if sections and sections[-1][-1]['layer']==a['layer'] and sections[-1][-1]['width']==width and math.hypot(sections[-1][-1]['x']-a['x'],sections[-1][-1]['y']-a['y'])<1e-8:
            sections[-1].append(bb)
        else:sections.append([aa,bb])
    trace_ids=[]
    for i,section in enumerate(sections):
        identifier=uid+f'_section_{i}';trace_ids.append(identifier)
        ids=[q[f] for q in [section[0],section[-1]] for f in ['start_pcb_port_id','end_pcb_port_id'] if f in q]
        records.append({'type':'pcb_trace','pcb_trace_id':identifier,'route':section,'pcb_port_ids':ids,**common})
    after=Copper(records);mm,rr=after.groups(key)
    new_roots={r for (e,_,_),r in zip(mm,rr) if e['type'] in ['pcb_smtpad','pcb_plated_hole']}
    if len(new_roots)>=len(islands):
        del records[before:]
        raise RuntimeError(name+': grid construction did not reduce physical islands')
    return {'net':name,'trace_ids':trace_ids,'added_vias':len(added),'expanded':expanded,
            'physical_islands_before':len(islands),'physical_islands_after':len(new_roots)}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--net');p.add_argument('--restart',action='store_true');args=p.parse_args()
    target=OUT/'board.circuit.json'
    source=OUT/'seeded.circuit.json' if args.restart or not target.exists() else target
    records=[e for e in json.loads(source.read_text()) if e['type']!='pcb_copper_pour']
    history_path=OUT/'connection-construction.json'
    history=[] if args.restart or not history_path.exists() else json.loads(history_path.read_text())
    order=['STATUS_B_C','STATUS_B_K','A_PLUS','B_PLUS','A_MINUS','B_MINUS','DIR','STEP','PD_VBUS','LOGIC_IN','DATA_VBUS','PD_CC1','PD_CC2']
    for name in order:
        if args.net and name!=args.net:continue
        for attempt in range(40):
            proof=connect(records,name,attempt)
            if proof is None:break
            history.append(proof)
            target.write_text(json.dumps(records,indent=2)+'\n');history_path.write_text(json.dumps(history,indent=2)+'\n')
            print(json.dumps(proof),flush=True)
        else:raise RuntimeError(name+': connection iteration limit')
    target.write_text(json.dumps(records,indent=2)+'\n')
