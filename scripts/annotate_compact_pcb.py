#!/usr/bin/env python3
"""Place readable native vector legends clear of pads, drills and screw heads."""
import argparse,json,math
from pathlib import Path
from shapely.geometry import LineString,Point,Polygon
from shapely.ops import unary_union
from pcb_geometry import pad_shape

ROOT=Path(__file__).resolve().parents[1]
LABELS=[('NEMA11 RP2040',0,7.5,.9),('PROTOTYPE 0.4',0,6,.8),
        ('PD 15V',-8.3,9.5,.85),('USB DATA',8.3,9.5,.85),
        ('1 A+ BLACK',0,-6.5,.8),('2 A- GREEN',0,-8,.8),
        ('3 B+ RED',0,-9.5,.8),('4 B- BLUE',0,-11,.8)]

def annotate(records):
    records[:]=[e for e in records if not e['type'].startswith('pcb_silkscreen_')]
    board=next(e for e in records if e['type']=='pcb_board')
    boundary=Polygon([(p['x'],p['y']) for p in board['outline']]).buffer(-.2)
    obstacles=[]
    for e in records:
        if e['type']=='pcb_smtpad' and e['layer']=='bottom' and not e.get('is_covered_with_solder_mask',False):obstacles.append(pad_shape(e).buffer(.05))
        elif e['type']=='pcb_plated_hole':obstacles.append(pad_shape(e).buffer(.05))
        elif e['type']=='pcb_hole':obstacles.append(pad_shape({**e,'shape':'circle','width':e['hole_diameter']}).buffer(.05))
        elif e['type']=='pcb_keepout':obstacles.append(Point(e['center']['x'],e['center']['y']).buffer(e['radius']))
    guard=unary_union(obstacles).buffer(.1501);font=json.loads((ROOT/'config/controller-silkscreen-font.json').read_text());stroke=.15
    source=next(e for e in records if e['type']=='source_component' and e['name']=='U_MCU');owner=next(e for e in records if e['type']=='pcb_component' and e['source_component_id']==source['source_component_id'])
    result=[];used=[]
    for i,(text,anchor_x,anchor_y,size) in enumerate(LABELS):
        cursor=0;segments=[]
        for char in text:
            if char!=' ' and char not in font['lineAlphabet']:raise ValueError('Missing font character '+char)
            for q in font['lineAlphabet'].get(char,[]):segments.append([(cursor+q['x1'],q['y1']),(cursor+q['x2'],q['y2'])])
            cursor+=font['glyphAdvanceRatio'].get(char,.692052)
        xs=[x for s in segments for x,y in s];ys=[y for s in segments for x,y in s];scale=(size-stroke)/(max(ys)-min(ys));cx=(max(xs)+min(xs))/2;cy=(max(ys)+min(ys))/2
        offsets=sorted([(dx*.25,dy*.25) for dx in range(-10,11) for dy in range(-10,11)],key=lambda p:(math.hypot(*p),abs(p[1]),p))
        chosen=None
        for dx,dy in offsets:
            x,y=anchor_x+dx,anchor_y+dy
            routes=[[dict(x=round(x-(px-cx)*scale,6),y=round(y+(py-cy)*scale,6)) for px,py in segment] for segment in segments]
            ink=unary_union([LineString([(p['x'],p['y']) for p in route]).buffer(stroke/2,quad_segs=32) for route in routes])
            if boundary.covers(ink) and not ink.intersects(guard) and not any(ink.distance(g)<.15 for g in used):chosen=(routes,ink,x,y);break
        if chosen is None:raise ValueError('No clear readable location for '+text)
        routes,ink,x,y=chosen;used.append(ink)
        for j,route in enumerate(routes):records.append(dict(type='pcb_silkscreen_path',pcb_silkscreen_path_id=f'compact_legend_{i}_{j}',route=route,stroke_width=stroke,layer='bottom',pcb_component_id=owner['pcb_component_id'],subcircuit_id=owner['subcircuit_id']))
        result.append(dict(text=text,layer='bottom',centre_mm=[x,y],character_height_mm=size,stroke_width_mm=stroke))
    return dict(scope='Functional bottom legends; component designators remain in separate assembly drawings',labels=result,minimum_mask_clearance_mm=.15,minimum_board_edge_clearance_mm=.2,top_function_labels_verified=False,manufacturing_release=False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);a=p.parse_args();r=json.loads(a.input.read_text());report=annotate(r);a.input.write_text(json.dumps(r,indent=2)+'\n');(a.input.parent/'silkscreen-construction.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(functional_legends=len(report['labels']),manufacturing_release=False)))
