#!/usr/bin/env python3
"""Construct anchored native ground pours; validate the resulting copper separately."""
import hashlib
import json
from pathlib import Path
from shapely.geometry import Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from pcb_geometry import Copper, LAYERS, pad_shape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/controller-pcb'


def fill(records):
    records[:] = [e for e in records if e['type'] != 'pcb_copper_pour']
    copper = Copper(records)
    elements = copper.elements()
    net = next(e for e in records if e['type'] == 'source_net' and e['name'] == 'GND')
    key = net['subcircuit_connectivity_map_key']
    board = next(e for e in records if e['type'] == 'pcb_board')
    boundary = Polygon([(p['x'], p['y']) for p in board['outline']]).buffer(-.35)
    exclusions = []
    for e in records:
        if e['type'] == 'pcb_keepout':
            assert e['shape'] == 'circle'
            # Leave positive allowance beyond the independently sampled circle.
            exclusions.append(Point(e['center']['x'], e['center']['y']).buffer(e['radius'] + .005, quad_segs=64))
        elif e['type'] == 'pcb_hole':
            exclusions.append(pad_shape({**e, 'shape': 'circle', 'width': e['hole_diameter']}).buffer(.30))
    regions = []
    for layer in copper.layers:
        anchors, obstacles = [], list(exclusions)
        for record, other, shapes in elements:
            if layer not in shapes:
                continue
            if other == key:
                anchors.append(shapes[layer])
            else:
                obstacles.append(shapes[layer].buffer(.20, quad_segs=16))
        area = boundary.difference(unary_union(obstacles))
        polygons = [area] if area.geom_type == 'Polygon' else list(area.geoms)
        coords = lambda ring: [(round(x, 6), round(y, 6)) for x, y in list(ring.coords)[:-1]]
        for i, polygon in enumerate(polygons):
            if polygon.geom_type != 'Polygon' or polygon.area < .02:
                continue
            exact = Polygon(coords(polygon.exterior), [coords(r) for r in polygon.interiors]).buffer(0)
            pieces = [exact] if exact.geom_type == 'Polygon' else list(exact.geoms)
            for j, piece in enumerate(pieces):
                if piece.area < .02 or not any(piece.intersects(a) for a in anchors):
                    continue
                piece = orient(piece, sign=-1)
                ring = lambda r: {'vertices': [{'x': x, 'y': y} for x, y in coords(r)]}
                records.append({'type': 'pcb_copper_pour', 'pcb_copper_pour_id': f'controller_ground_{layer}_{i}_{j}',
                                'source_net_id': net['source_net_id'], 'subcircuit_connectivity_map_key': key,
                                'subcircuit_id': net['subcircuit_id'], 'layer': layer, 'shape': 'brep',
                                'covered_with_solder_mask': True, 'brep_shape': {'outer_ring': ring(piece.exterior),
                                'inner_rings': [ring(r) for r in piece.interiors]}})
                regions.append({'layer': layer, 'net': 'GND', 'area_mm2': piece.area})
    return regions


if __name__ == '__main__':
    path = OUT / 'board.circuit.json'
    records = json.loads(path.read_text())
    regions = fill(records)
    path.write_text(json.dumps(records, indent=2) + '\n')
    report = {'scope': 'Ground pour construction; independent checks are required',
              'clearance_mm': .20, 'board_edge_mm': .35, 'regions': regions,
              'circuit_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'manufacturing_release': False}
    (OUT / 'ground-construction.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'regions': len(regions), 'largest_inner1_mm2': max(r['area_mm2'] for r in regions if r['layer'] == 'inner1')}))
