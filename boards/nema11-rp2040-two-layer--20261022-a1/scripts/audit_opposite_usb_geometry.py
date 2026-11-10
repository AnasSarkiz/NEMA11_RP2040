#!/usr/bin/env python3
"""Conservative copper, courtyard, through-hole and NPTH placement screen.

Does not waive native USB courtyard boundary findings or qualify mating,
assembly, routing, tolerances or manufacture. Historical audit remains unchanged.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
_spec=importlib.util.spec_from_file_location("historical_geometry", Path(__file__).with_name("audit_placement_geometry.py"))
_legacy=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_legacy)
legacy_audit,geometry_bounds,gap,EPS=_legacy.audit,_legacy.geometry_bounds,_legacy.gap,_legacy.EPS

BOARD_DIR = Path(__file__).resolve().parents[1]
REFERENCE = 'references/opposite-usb-20261110/anchor-reference.json'


def circle_bounds_gap(x, y, radius, bounds):
    return math.hypot(*[max(bounds['lo'][k]-v, v-bounds['hi'][k], 0) for k,v in enumerate((x,y))])-radius


def overlaps(a,b):
    return all(min(a['hi'][k], b['hi'][k])-max(a['lo'][k],b['lo'][k]) > 0 for k in (0,1))


def point_segment_distance(x,y,a,b):
    dx,dy=b['x']-a['x'],b['y']-a['y']
    length=dx*dx+dy*dy
    t=max(0,min(1,((x-a['x'])*dx+(y-a['y'])*dy)/length)) if length else 0
    return math.hypot(x-a['x']-t*dx,y-a['y']-t*dy)


def circle_outline_gap(x,y,radius,outline):
    """Signed circle-edge to filled genuine courtyard; no probe diameter assumed."""
    inside=False;distance=math.inf
    for a,b in zip(outline,outline[1:]+outline[:1]):
        distance=min(distance,point_segment_distance(x,y,a,b))
        if (a['y']>y)!=(b['y']>y) and x < a['x']+(y-a['y'])*(b['x']-a['x'])/(b['y']-a['y']):inside=not inside
    inside=inside or distance==0
    return (-distance if inside else distance)-radius,inside


def audit(circuit, placement, baseline):
    report = legacy_audit(circuit, placement, baseline)
    names = {e['source_component_id']: e['name'] for e in circuit if e['type']=='source_component'}
    components = {e['pcb_component_id']: e for e in circuit if e['type']=='pcb_component'}
    if len(names)!=99 or len(components)!=99:
        raise ValueError('Expected complete unchanged population of 99 components')
    for comp in components.values():
        name=names[comp['source_component_id']]
        pose=placement['placements'][name]
        origin=comp['footprint_origin']
        if not all(math.isfinite(v) for v in (origin['x'],origin['y'],comp['rotation'])):
            raise ValueError('Nonfinite emitted component pose')
        if (abs(origin['x']-pose['pcbX'])>EPS or abs(origin['y']-pose['pcbY'])>EPS or comp['rotation']%360!=pose['pcbRotation']%360 or comp['layer']!=pose['layer']):
            raise ValueError('Emitted component pose does not match active placement: '+name)
    items=[]
    for e in circuit:
        if e['type'] not in {'pcb_smtpad','pcb_plated_hole','pcb_courtyard_outline'}:
            continue
        comp=components[e['pcb_component_id']]
        lo,hi=geometry_bounds(e)
        items.append(dict(name=names[comp['source_component_id']],lo=lo,hi=hi,
            layers=e.get('layers',[e.get('layer')]),kind=e['type'],
            id=e[e['type']+'_id'],dnp=comp.get('do_not_place',False),outline=e.get('outline')))
    bodies=[e for e in items if e['kind']=='pcb_courtyard_outline' and not e['dnp']]
    pads=[e for e in items if e['kind']!='pcb_courtyard_outline']
    body_pairs=[]
    for i,a in enumerate(bodies):
        for b in bodies[:i]:
            if set(a['layers'])&set(b['layers']) and a['name']!=b['name'] and overlaps(a,b):
                body_pairs.append([a['name'],b['name']])
    tab_pairs=[]
    for a in bodies:
        for b in pads:
            if b['kind']=='pcb_plated_hole' and a['name']!=b['name'] and overlaps(a,b):
                tab_pairs.append([a['name'],b['name'],b['id']])
    testpoint_gaps=[];testpoint_overlaps=[];testpoint_centers=[]
    for e in circuit:
        if e['type']!='pcb_smtpad':continue
        name=names[components[e['pcb_component_id']]['source_component_id']]
        if not name.startswith('TP_'):continue
        if e.get('shape')!='circle' or not math.isfinite(e.get('radius',float('nan'))) or e['radius']<=0:
            raise ValueError('Expected genuine circular testpoint copper')
        distances=[]
        for body in bodies:
            if e['layer'] not in body['layers']:continue
            distance,inside=circle_outline_gap(e['x'],e['y'],e['radius'],body['outline'])
            distances.append((distance,body['name']))
            if inside:testpoint_centers.append([name,body['name']])
            if distance<0:testpoint_overlaps.append(dict(testpoint=name,body=body['name'],pad_edge_gap_mm=distance))
        distance,body=min(distances)
        testpoint_gaps.append(dict(testpoint=name,nearest_fitted_courtyard=body,pad_edge_gap_mm=distance))
    if {e['testpoint'] for e in testpoint_gaps}!={'TP_BOOT','TP_BOOT_GND','TP_3V3','TP_GND','TP_SWCLK','TP_SWDIO','TP_RUN'} or len(testpoint_gaps)!=7:
        raise ValueError('Expected all seven actual test pads')
    holes=[e for e in circuit if e['type']=='pcb_hole']
    if any(not all(math.isfinite(e[k]) for k in ('x','y','hole_diameter')) or e['hole_diameter']<=0 for e in holes):
        raise ValueError('Nonfinite or nonpositive hole geometry')
    mounts=[e for e in holes if not e.get('pcb_component_id')]
    axes={(x,y) for x in (-11.5,11.5) for y in (-11.5,11.5)}
    if len(mounts)!=4 or {(e['x'],e['y']) for e in mounts}!=axes or any(e.get('hole_shape')!='circle' or abs(e['hole_diameter']-2.7)>EPS for e in mounts):
        raise ValueError('Expected unchanged four 2.7mm motor-axis holes')
    locators=[e for e in holes if e.get('pcb_component_id')]
    expected=[]
    for name in ('J_PD','J_DATA'):
        pose=placement['placements'][name]
        a=math.radians(pose['pcbRotation'])
        for x in (-2.899918,2.899918):
            y=.9055672
            expected.append((name,pose['pcbX']+math.cos(a)*x-math.sin(a)*y,pose['pcbY']+math.sin(a)*x+math.cos(a)*y))
    actual=[]
    for e in locators:
        name=names[components[e['pcb_component_id']]['source_component_id']]
        if e.get('hole_shape')!='circle' or not math.isfinite(e['hole_diameter']) or abs(e['hole_diameter']-.5999988)>EPS:
            raise ValueError('Unexpected genuine USB locator shape or diameter')
        actual.append((name,e['x'],e['y']))
    if len(actual)!=4 or any(not any(a[0]==b[0] and math.hypot(a[1]-b[1],a[2]-b[2])<EPS for b in actual) for a in expected):
        raise ValueError('Missing or relocated genuine USB locator holes')
    hole_copper=[];hole_bodies=[];minimum=math.inf;body_hole_min=math.inf;own_min=math.inf;own_pairs=[]
    for h in holes:
        name=names[components[h['pcb_component_id']]['source_component_id']] if h.get('pcb_component_id') else h['pcb_hole_id']
        for p in pads+bodies:
            own=p['name']==name
            if own and p['kind']=='pcb_courtyard_outline':continue
            distance=circle_bounds_gap(h['x'],h['y'],h['hole_diameter']/2,p)
            if own:
                own_min=min(own_min,distance)
                if distance < .15:own_pairs.append(dict(hole=h['pcb_hole_id'],id=p['id'],gap_mm=distance))
                continue
            if p['kind']=='pcb_courtyard_outline':
                body_hole_min=min(body_hole_min,distance)
                if distance < 0:hole_bodies.append(dict(hole=h['pcb_hole_id'],component=p['name'],gap_mm=distance))
            else:
                minimum=min(minimum,distance)
                # Positive margin stronger than the board's 0.15mm copper rule.
                if distance < .25:hole_copper.append(dict(hole=h['pcb_hole_id'],component=p['name'],id=p['id'],gap_mm=distance))
    board=next(e for e in circuit if e['type']=='pcb_board')
    if board.get('center')!={'x':0,'y':0}:raise ValueError('Expected centered board at origin')
    hole_edge=min(14-abs(h[k])-h['hole_diameter']/2 for h in holes for k in ('x','y'))
    body_edge=min(min(e['lo'][k]+14,14-e['hi'][k]) for e in bodies if e['name'] not in {'J_PD','J_DATA'} for k in (0,1))
    if (board['width'],board['height'])!=(28,28):raise ValueError('Board envelope changed')
    all_poses=placement['placements']==baseline['placements']
    def limiting_pair(pairs):
        distance,a,b=min(((gap(a,b),a,b) for a,b in pairs),key=lambda x:x[0])
        return dict(a=a['name'],b=b['name'],a_geometry_id=a['id'],b_geometry_id=b['id'],conservative_gap_mm=distance)
    body_limit=limiting_pair((a,b) for i,a in enumerate(bodies) for b in bodies[:i] if set(a['layers'])&set(b['layers']))
    tab_limit=limiting_pair((a,b) for a in bodies for b in pads if b['kind']=='pcb_plated_hole' and a['name']!=b['name'])
    report.update(scope='Conservative imported-geometry placement screen; not native boundary, routing, mating, assembly, tolerance or manufacturing approval.',
        reviewed_full_placement_unchanged=all_poses,
        testpoint_pad_edge_to_fitted_courtyard=testpoint_gaps,
        testpoint_pad_courtyard_overlaps=testpoint_overlaps,
        testpoint_centers_inside_fitted_courtyards=testpoint_centers,
        probe_access_qualified=False,
        testpoint_screen_scope='Actual copper pad versus genuine fitted courtyard, not a probe diameter or complete probing-access qualification.',
        fitted_courtyard_limiting_pair=body_limit,plated_tab_body_limiting_pair=tab_limit,
        clearance_qualification='Nominal imported-geometry screen only; small positive courtyard/tab gaps are not tolerance-qualified.',
        fitted_courtyard_overlap_pairs=body_pairs,plated_tab_body_overlap_pairs=tab_pairs,
        npth_body_overlaps=hole_bodies,npth_own_copper_pairs_below_015mm=own_pairs,npth_min_own_copper_gap_mm=own_min,npth_copper_pairs_below_025mm=hole_copper,
        npth_min_conservative_copper_gap_mm=minimum,
        genuine_usb_locator_geometry_verified=True,
        copper_minimum_rule_mm=.15,npth_other_copper_minimum_rule_mm=.25,npth_own_copper_minimum_rule_mm=.15,npth_board_edge_minimum_rule_mm=.25,copper_board_edge_minimum_rule_mm=.25,
        fitted_courtyard_min_conservative_gap_mm=min(gap(a,b) for i,a in enumerate(bodies) for b in bodies[:i] if set(a['layers'])&set(b['layers'])),
        plated_tab_body_min_conservative_gap_mm=min(gap(a,b) for a in bodies for b in pads if b['kind']=='pcb_plated_hole' and a['name']!=b['name']),
        npth_body_min_conservative_gap_mm=body_hole_min,
        npth_min_board_edge_gap_mm=hole_edge,
        usb_courtyard_edge_gaps_mm={e['name']:min(min(e['lo'][k]+14,14-e['hi'][k]) for k in (0,1)) for e in bodies if e['name'] in {'J_PD','J_DATA'}},
        non_usb_fitted_courtyard_min_edge_gap_mm=body_edge,
        usb_courtyard_boundary_approval=False)
    report['independent_geometry_pass']=bool(report['independent_geometry_pass'] and all_poses and not testpoint_overlaps and not testpoint_centers and not body_pairs and not tab_pairs and not hole_bodies and not hole_copper and not own_pairs and hole_edge>=.25 and body_edge>=0 and report['copper_min_conservative_AABB_gap_mm']>=.15 and report['copper_min_conservative_edge_gap_mm']>=.25 and report['minimum_conservative_bolt_head_envelope_gap_mm']>=0)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--circuit',type=Path,default=BOARD_DIR/'dist/index/circuit.json')
    p.add_argument('--placement',type=Path,default=BOARD_DIR/'config/placement.json')
    p.add_argument('--baseline',type=Path,default=BOARD_DIR/REFERENCE)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    try:
        paths=[args.circuit,args.placement,args.baseline]
        r=audit(*(json.loads(x.read_text()) for x in paths))
        r['input_sha256']={k:hashlib.sha256(x.read_bytes()).hexdigest() for k,x in zip(('circuit','placement','baseline'),paths)}
        out=json.dumps(r,indent=2,allow_nan=False)+'\n'
        if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(out)
        print(out,end='');return 0 if r['independent_geometry_pass'] else 1
    except (ValueError,KeyError,TypeError,OSError) as e:
        print(json.dumps({'independent_geometry_pass':False,'error':str(e)}));return 2


if __name__=='__main__':raise SystemExit(main())
