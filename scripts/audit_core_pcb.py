#!/usr/bin/env python3
"""Independent per-layer copper audit; native net IDs never imply physical contact."""
import hashlib
import json
from collections import Counter
from pathlib import Path
from shapely.geometry import box, Polygon
from shapely.strtree import STRtree
from pcb_geometry import Copper, LAYERS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/rp2040-pcb'


def audit(records):
    copper = Copper(records)
    elements = copper.elements()
    errors = []
    board = next(e for e in records if e['type'] == 'pcb_board')
    boundary = box(-board['width']/2+.25, -board['height']/2+.25,
                   board['width']/2-.25, board['height']/2-.25)
    if board.get('outline'):
        boundary = Polygon([(p['x'], p['y']) for p in board['outline']]).buffer(-.25)
    for record, _, shapes in elements:
        for layer, shape in shapes.items():
            if not shape.is_valid:
                errors.append({'type': 'invalid_geometry', 'id': record[record['type']+'_id']})
            if not boundary.buffer(1e-6).covers(shape):
                errors.append({'type': 'board_edge', 'id': record[record['type']+'_id'], 'layer': layer})
        if record['type'] == 'pcb_via' and (record['hole_diameter'] < .30-1e-8 or record['outer_diameter'] < .45-1e-8):
            errors.append({'type': 'via_minimum', 'id': record['pcb_via_id']})
        if record['type'] == 'pcb_trace' and min(p['width'] for p in record['route']) < .16-1e-8:
            errors.append({'type': 'trace_minimum', 'id': record['pcb_trace_id']})
    seen = set()
    for layer in LAYERS:
        local = [(record, key, shapes[layer]) for record, key, shapes in elements if layer in shapes]
        shapes = [e[2] for e in local]
        tree = STRtree(shapes)
        for i, (a, ka, sa) in enumerate(local):
            for j in tree.query(sa.buffer(.15)):
                if j <= i:
                    continue
                b, kb, sb = local[j]
                if ka is not None and ka == kb:
                    continue
                aid, bid = a[a['type']+'_id'], b[b['type']+'_id']
                if aid == bid:
                    continue
                distance = sa.distance(sb)
                pair = (layer, *sorted([aid, bid]))
                if distance < .15-2e-6 and pair not in seen:
                    seen.add(pair)
                    errors.append({'type': 'short' if sa.intersection(sb).area > 1e-9 else 'clearance',
                                   'layer': layer, 'a': aid, 'b': bid,
                                   'nets': [copper.nets.get(ka), copper.nets.get(kb)], 'gap_mm': distance})
    connectivity = copper.connectivity()
    errors.extend({'type': 'disconnected_net', **e} for e in connectivity)
    return {'scope': 'MCU subsystem copper only; external controller interfaces remain open',
            'method': 'Shapely per-layer pad/trace/annulus/pour geometry; plated barrels join layers',
            'clearance_mm': .15, 'board_edge_mm': .25, 'via_drill_pad_mm': [.30, .45],
            'error_counts': dict(Counter(e['type'] for e in errors)), 'errors': errors,
            'manufacturing_release': False}


if __name__ == '__main__':
    path = OUT / 'board.circuit.json'
    report = audit(json.loads(path.read_text()))
    report['circuit_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT / 'independent-copper-audit.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'error_counts': report['error_counts'], 'errors': len(report['errors'])}))
    raise SystemExit(bool(report['errors']))
