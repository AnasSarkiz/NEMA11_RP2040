#!/usr/bin/env python3
"""Offline nominal imported-mesh spacing screen. No network or native build."""
import argparse
import collections
import hashlib
import itertools
import json
import math
from pathlib import Path


def cross(o, a, b):
    return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])


def hull(points):
    points = sorted(set(tuple(p) for p in points))
    if len(points) < 3:
        raise ValueError('Degenerate model projection')
    lower, upper = [], []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    result = lower[:-1]+upper[:-1]
    if len(result) < 3:
        raise ValueError('Collinear model projection')
    return result


def point_segment(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    t = max(0, min(1, ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
    q = (a[0]+t*dx, a[1]+t*dy)
    return math.dist(p, q), p, q


def convex_distance(a, b):
    separated = False
    for polygon in (a, b):
        for p, q in zip(polygon, polygon[1:]+polygon[:1]):
            axis = (-(q[1]-p[1]), q[0]-p[0])
            pa = [v[0]*axis[0]+v[1]*axis[1] for v in a]
            pb = [v[0]*axis[0]+v[1]*axis[1] for v in b]
            separated |= max(pa) < min(pb) or max(pb) < min(pa)
    if not separated:
        return 0.0, None, None
    candidates = [point_segment(p, q, r) for p in a for q, r in zip(b, b[1:]+b[:1])]
    candidates += [(d, r, q) for p in b for q0, r0 in zip(a, a[1:]+a[:1]) for d, q, r in [point_segment(p, q0, r0)]]
    return min(candidates, key=lambda v: v[0])


def transform(cad, point):
    if cad.get('model_board_normal_direction') or cad.get('size') or cad.get('model_unit_to_mm_scale_factor', 1) != 1:
        raise ValueError('Unsupported authored model orientation, box fit or scale')
    rotation = cad['rotation']
    if rotation['x'] != 0 or rotation['y'] not in (0, 180):
        raise ValueError('Unsupported X/Y rotation')
    origin, position = cad['model_origin_position'], cad['position']
    x, y, z = [point[k]-origin[axis] for k, axis in enumerate('xyz')]
    theta = math.radians(rotation['z'])
    c, s = math.cos(theta), math.sin(theta)
    x, y = c*x-s*y, s*x+c*y
    # Official loader uses XYZ Euler convention: R_y follows R_z here.
    if rotation['y'] == 180:
        x, z = -x, -z
    return [x+position['x'], y+position['y'], z+position['z']]


def models(circuit, board):
    source = {e['source_component_id']: e for e in circuit if e['type'] == 'source_component'}
    pcb = {e['pcb_component_id']: e for e in circuit if e['type'] == 'pcb_component'}
    output = []
    for cad in [e for e in circuit if e['type'] == 'cad_component']:
        p = pcb[cad['pcb_component_id']]
        if p.get('do_not_place'):
            raise ValueError('Unexpected fitted CAD record for DNP component')
        if (cad['rotation']['y'] == 180) != (p['layer'] == 'bottom'):
            raise ValueError('Layer and native CAD orientation disagree')
        model = (board/cad['model_obj_url']).resolve()
        if not model.is_relative_to(board/'imports') or model.suffix != '.obj':
            raise ValueError('Only local genuine OBJ imports allowed')
        raw = model.read_bytes()
        vertices = [transform(cad, list(map(float, line.split()[1:4]))) for line in raw.decode().splitlines() if line.startswith('v ')]
        if not vertices or any(not all(math.isfinite(x) for x in v) for v in vertices):
            raise ValueError('Empty or nonfinite model vertices')
        low, high = [[f(v[k] for v in vertices) for k in range(3)] for f in (min, max)]
        output.append(dict(name=source[cad['source_component_id']]['name'], layer=p['layer'],
            model=str(model.relative_to(board)), model_sha256=hashlib.sha256(raw).hexdigest(),
            min=low, max=high, projected_convex_hull=hull(v[:2] for v in vertices), vertex_count=len(vertices)))
    fitted = {e['pcb_component_id'] for e in pcb.values() if not e.get('do_not_place')}
    assert {e['pcb_component_id'] for e in circuit if e['type']=='cad_component'} == fitted
    return output


def pairs(items, same_face=True):
    output = []
    for a, b in itertools.combinations(items, 2):
        if (a['layer'] == b['layer']) != same_face:
            continue
        distance, p, q = convex_distance(a['projected_convex_hull'], b['projected_convex_hull'])
        output.append(dict(a=a['name'], b=b['name'], layer=a['layer'] if same_face else 'opposite',
            conservative_whole_model_convex_gap_mm=distance, closest_hull_points=[p,q]))
    return sorted(output, key=lambda e: e['conservative_whole_model_convex_gap_mm'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board',type=Path,required=True)
    parser.add_argument('--native',type=Path,required=True)
    parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--official',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    board=args.board.resolve()
    baseline=models(json.loads(args.baseline.read_bytes()),board)
    official={e['name']:e for e in json.loads(args.official.read_bytes())}
    diffs=[abs(e[key][k]-official[e['name']][key][k]) for e in baseline for key in ('min','max') for k in range(3)]
    assert len(official)==len(baseline)==89
    assert max(diffs)<1e-8, 'Independent transform disagrees with archived official loader'
    native_bytes=args.native.read_bytes()
    circuit=json.loads(native_bytes)
    current=models(circuit,board)
    same=pairs(current)
    opposite=pairs(current,False)
    report=dict(scope='Offline nominal whole imported OBJ projected convex hulls, including leads. Conservative lower bounds, not manufacturer maximum body dimensions or assembly approval.',
        native_sha256=hashlib.sha256(native_bytes).hexdigest(), baseline_sha256=hashlib.sha256(args.baseline.read_bytes()).hexdigest(),
        official_loader_bounds_sha256=hashlib.sha256(args.official.read_bytes()).hexdigest(),
        archived_official_loader_transform_max_difference_mm=max(diffs),
        fitted_sides=dict(collections.Counter(e['layer'] for e in current)),
        dnp_components_excluded=sum(e['type']=='pcb_component' and e.get('do_not_place',False) for e in circuit),
        same_face_pairs_checked=len(same), same_face_pairs_below_02mm=[e for e in same if e['conservative_whole_model_convex_gap_mm']<.2-1e-9],
        nearest_same_face_pairs=same[:30], opposite_face_projection_overlaps_separate=sum(e['conservative_whole_model_convex_gap_mm']==0 for e in opposite),
        opposite_face_pairs_excluded_from_same_face_test=len(opposite), components=current, manufacturing_approved=False)
    assert args.native.read_bytes()==native_bytes
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('components','nearest_same_face_pairs')},indent=2))


if __name__=='__main__':
    main()
