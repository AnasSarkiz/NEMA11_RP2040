#!/usr/bin/env python3
"""Conservative AABB audit of unmodified emitted geometry, including DNP copper.

This is not an exact polygon, routing, assembly or mechanical-fit checker. Bounds
are supersets of copper/body courtyards, so gaps are conservative lower bounds.
Rotated SMT dimensions are local: installed circuit-to-svg applies a centered
ccw_rotation transform for rotated_rect/rotated_pill; core carries that rotation.
"""
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path

BOARD_DIR = Path(__file__).resolve().parents[1]
FROZEN = ('J_PD', 'J_DATA', 'J_MOTOR', 'C_BULK', 'U_DRV', 'U_ESD', 'C_ESD', 'U_ENCODER')
EPS = 1e-6


def positive(value, label):
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f'{label} must be positive and finite')
    return value


def geometry_bounds(element):
    """Return (lo, hi) in world axes; reject unknown or malformed geometry."""
    kind, shape = element['type'], element.get('shape')
    if kind == 'pcb_courtyard_outline' or (kind == 'pcb_smtpad' and shape == 'polygon'):
        points = element.get('outline', element.get('points'))
        if not points or len(points) < 3:
            raise ValueError('Polygon must contain at least three points')
        coords = [(float(p['x']), float(p['y'])) for p in points]
        if not all(math.isfinite(v) for p in coords for v in p):
            raise ValueError('Nonfinite polygon coordinate')
        return ([min(p[k] for p in coords) for k in (0, 1)],
                [max(p[k] for p in coords) for k in (0, 1)])
    if kind == 'pcb_smtpad':
        if shape not in {'rect', 'rotated_rect', 'pill', 'rotated_pill', 'circle'}:
            raise ValueError(f'Unsupported SMT shape: {shape}')
        if shape == 'circle':
            width = height = 2 * positive(element['radius'], 'radius')
        else:
            width = positive(element['width'], 'width')
            height = positive(element['height'], 'height')
        rotation = element.get('ccw_rotation', 0) if shape in {'rotated_rect', 'rotated_pill'} else 0
    elif kind == 'pcb_plated_hole':
        if shape == 'circle':
            width = height = positive(element['outer_diameter'], 'outer_diameter')
            rotation = 0
        elif shape in {'pill', 'oval', 'rect'}:
            width = positive(element['outer_width'], 'outer_width')
            height = positive(element['outer_height'], 'outer_height')
            rotation = element.get('ccw_rotation', 0)
        else:
            raise ValueError(f'Unsupported plated-hole shape: {shape}')
    else:
        raise ValueError(f'Unsupported geometry type: {kind}')
    x, y, rotation = float(element['x']), float(element['y']), float(rotation)
    if not all(math.isfinite(v) for v in (x, y, rotation)):
        raise ValueError('Nonfinite geometry coordinate or rotation')
    theta = math.radians(rotation)
    c, s = abs(math.cos(theta)), abs(math.sin(theta))
    width, height = width*c + height*s, width*s + height*c
    return [x-width/2, y-height/2], [x+width/2, y+height/2]


def gap(a, b):
    return math.hypot(*[max(a['lo'][k]-b['hi'][k], b['lo'][k]-a['hi'][k], 0) for k in (0, 1)])


def audit(circuit, placement, baseline):
    sources = {e['source_component_id']: e['name'] for e in circuit if e['type'] == 'source_component'}
    components = {e['pcb_component_id']: e for e in circuit if e['type'] == 'pcb_component'}
    boards = [e for e in circuit if e['type'] == 'pcb_board']
    if len(boards) != 1:
        raise ValueError('Expected exactly one native PCB board')
    board = boards[0]
    width, height = positive(board['width'], 'board width'), positive(board['height'], 'board height')
    cx, cy = board['center']['x'], board['center']['y']
    board_lo, board_hi = (cx-width/2, cy-height/2), (cx+width/2, cy+height/2)
    keepouts = [e for e in circuit if e['type'] == 'pcb_keepout']
    expected = {(-11.5, -11.5), (-11.5, 11.5), (11.5, -11.5), (11.5, 11.5)}
    if len(keepouts) != 4 or any(e.get('shape') != 'circle' or abs(e['radius']-2.35) > EPS or set(e['layers']) != {'top', 'bottom'} for e in keepouts):
        raise ValueError('Expected four unchanged R2.35 two-side bolt keepouts')
    if {(e['center']['x'], e['center']['y']) for e in keepouts} != expected:
        raise ValueError('Bolt axes differ from preserved geometry')
    pads, courtyards = [], []
    for e in circuit:
        if e['type'] not in {'pcb_smtpad', 'pcb_plated_hole', 'pcb_courtyard_outline'}:
            continue
        component = components[e['pcb_component_id']]
        lo, hi = geometry_bounds(e)
        layers = e.get('layers', [e.get('layer')])
        if not layers or any(layer not in {'top', 'bottom'} for layer in layers):
            raise ValueError('Unrecognized geometry layer')
        item = dict(name=sources[component['source_component_id']], lo=lo, hi=hi,
                    layers=layers, id=e[e['type']+'_id'], dnp=component.get('do_not_place', False))
        (courtyards if e['type'] == 'pcb_courtyard_outline' else pads).append(item)
    if not pads:
        raise ValueError('No native copper geometry')
    violations, dnp_min, minimum = [], math.inf, math.inf
    for i, a in enumerate(pads):
        for b in pads[:i]:
            if a['name'] == b['name'] or not set(a['layers']).intersection(b['layers']):
                continue
            distance = gap(a, b)
            minimum = min(minimum, distance)
            if a['dnp'] or b['dnp']:
                dnp_min = min(dnp_min, distance)
            if distance < .15-EPS:
                violations.append(dict(a=a['name'], b=b['name'], a_id=a['id'], b_id=b['id'], conservative_AABB_gap_mm=distance))
    edge = min(min(a['lo'][k]-board_lo[k], board_hi[k]-a['hi'][k]) for a in pads for k in (0, 1))
    bolt_margin = min(math.hypot(*[max(a['lo'][k]-e['center'][axis], e['center'][axis]-a['hi'][k], 0) for k, axis in enumerate(('x', 'y'))])-e['radius'] for a in pads+courtyards for e in keepouts if set(a['layers']).intersection(e['layers']))
    anchors = all(placement['placements'][n] == baseline['placements'][n] for n in FROZEN)
    rotated = [e for e in circuit if e['type'] == 'pcb_smtpad' and e.get('shape') in {'rotated_rect', 'rotated_pill'}]
    result = dict(scope='Conservative AABB geometry only; no mechanical/assembly/routing acceptance.',
        source_count=len(sources), pcb_count=len(components),
        fitted_sides=dict(collections.Counter(e['layer'] for e in components.values() if not e.get('do_not_place'))),
        frozen_anchors_unchanged=anchors, pcb_traces=sum(e['type']=='pcb_trace' for e in circuit),
        pcb_vias=sum(e['type']=='pcb_via' for e in circuit),
        copper_min_conservative_AABB_gap_mm=minimum if math.isfinite(minimum) else None,
        DNP_inclusive_min_conservative_AABB_gap_mm=dnp_min if math.isfinite(dnp_min) else None,
        copper_min_conservative_edge_gap_mm=edge, minimum_conservative_bolt_head_envelope_gap_mm=bolt_margin,
        conservative_pad_pairs_below_015mm=violations,
        native_top_level_errors=dict(collections.Counter(e['type'] for e in circuit if 'error' in e['type'])),
        native_nested_errors=dict(collections.Counter(r['type'] for e in circuit for r in e.get('related_errors', []))),
        rotated_smt_shape_counts=dict(collections.Counter(f"{e['shape']}:{e.get('ccw_rotation',0)}" for e in rotated)))
    result['independent_geometry_pass'] = not violations and edge >= .25-EPS and bolt_margin >= -EPS and anchors
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--circuit', type=Path, default=BOARD_DIR/'dist/index/circuit.json')
    parser.add_argument('--placement', type=Path, default=BOARD_DIR/'config/placement.json')
    parser.add_argument('--baseline', type=Path, default=BOARD_DIR/'references/reconstructed-placement-final/baseline.placement.json')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        paths = [args.circuit, args.placement, args.baseline]
        report = audit(*(json.loads(path.read_text()) for path in paths))
        report['input_sha256'] = {label: hashlib.sha256(path.read_bytes()).hexdigest() for label, path in zip(('circuit', 'placement', 'baseline'), paths)}
        output = json.dumps(report, indent=2, allow_nan=False)+'\n'
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output)
        print(output, end='')
        return 0 if report['independent_geometry_pass'] else 1
    except (ValueError, KeyError, OSError, TypeError) as error:
        print(json.dumps({'independent_geometry_pass': False, 'error': str(error)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
