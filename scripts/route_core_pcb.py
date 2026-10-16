#!/usr/bin/env python3
"""Transfer checked native MCU corridors, then refill ground for this PCB alone."""
import copy
import hashlib
import json
from pathlib import Path
from collections import Counter
from shapely.geometry import Point, Polygon, box, LineString
import math
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from shapely.strtree import STRtree
from pcb_geometry import Copper, pad_shape, LAYERS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/rp2040-pcb'


def build(base, seed):
    result = copy.deepcopy(base)
    source = {e['source_component_id']: e['name'] for e in base if e['type'] == 'source_component'}
    sp = {e['source_port_id']: e for e in base if e['type'] == 'source_port'}
    pp = {e['pcb_port_id']: e for e in base if e['type'] == 'pcb_port'}
    ports = {(source[sp[e['source_port_id']]['source_component_id']], sp[e['source_port_id']]['pin_number']): e
             for e in pp.values()}
    pads = {(source[sp[pp[e['pcb_port_id']]['source_port_id']]['source_component_id']],
             sp[pp[e['pcb_port_id']]['source_port_id']]['pin_number']): e
            for e in base if e['type'] == 'pcb_smtpad'}
    for expected in seed['core_reference_pads']:
        current = pads[(expected['component'], expected['pin'])]
        assert pad_shape(current).hausdorff_distance(pad_shape(expected['pad'])) < 1e-6, expected['component']
    newnets = {e['name']: e for e in base if e['type'] == 'source_net'}
    source_traces = {}
    for name, net in newnets.items():
        identifier = 'source_trace_core_route_' + name
        source_traces[net['source_net_id']] = identifier
        result.append({'type': 'source_trace', 'source_trace_id': identifier,
                       'connected_source_port_ids': [], 'connected_source_net_ids': [net['source_net_id']],
                       'subcircuit_connectivity_map_key': net['subcircuit_connectivity_map_key'],
                       'subcircuit_id': net['subcircuit_id']})
    remap = {}
    for identifier, old in seed['port_by_id'].items():
        current = ports.get((old['component'], old['pin']))
        if current:
            remap[identifier] = current['pcb_port_id']
    for raw in seed['routing']:
        e = copy.deepcopy(raw)
        net = newnets[seed['net_by_key'][e['subcircuit_connectivity_map_key']]]
        e['source_net_id'] = net['source_net_id']
        e['subcircuit_connectivity_map_key'] = net['subcircuit_connectivity_map_key']
        e['source_trace_id'] = source_traces[net['source_net_id']]
        identifier = e['type'] + '_id'
        e[identifier] = 'core_' + e[identifier]
        if e['type'] == 'pcb_trace':
            for point in e['route']:
                for field in ['start_pcb_port_id', 'end_pcb_port_id']:
                    old = point.pop(field, None)
                    if old in remap:
                        point[field] = remap[old]
            e['pcb_port_ids'] = [remap[p] for p in raw.get('pcb_port_ids', []) if p in remap]
        result.append(e)
    return result


def prune_absent_branches(records):
    """Delete absent-component supply stubs flagged by the prior native DRC.

    Each deletion must preserve every actual pad's physical connectivity. The
    list is a reviewed routing edit, not an exclusion from the final checks.
    """
    edits = ROOT / 'src/pcb/remove-absent-component-stubs.json'
    if not edits.exists():
        return []
    removed = []
    for identifier in json.loads(edits.read_text()):
        candidate = [e for e in records if e.get('pcb_trace_id') != identifier]
        if len(candidate) == len(records):
            raise ValueError('Unknown route edit: ' + identifier)
        records[:] = candidate
        removed.append(identifier)
    return removed


def bind_physical_route_groups(records):
    """Bind native trace metadata to a pad in its actual copper group.

    Remove copper groups serving no retained source pad before adding planes.
    Net identity alone is never accepted as evidence of physical contact.
    """
    geometry = Copper(records)
    by_port = {port: e['source_trace_id'] for e in records if e['type'] == 'source_trace'
               and e.get('connected_source_port_ids') for port in e['connected_source_port_ids']}
    keep, bindings = set(), {}
    orphan = set()
    for key in geometry.nets:
        elements, roots = geometry.groups(key)
        for root in sorted(set(roots)):
            group = [e for e, r in zip(elements, roots) if r == root]
            pads = [e[0] for e in group if e[0]['type'] == 'pcb_smtpad']
            routes = [e[0] for e in group if e[0]['type'] in ['pcb_trace', 'pcb_via']]
            for route in routes:
                identifier = route[route['type']+'_id']
                if pads:
                    keep.add(identifier)
                    source_port = geometry.ports[pads[0]['pcb_port_id']]['source_port_id']
                    bindings[identifier] = by_port[source_port]
                else:
                    orphan.add(identifier)
    remove = orphan - keep
    records[:] = [e for e in records if e.get(e['type']+'_id') not in remove
                  and not (e['type'] == 'source_trace' and e['source_trace_id'].startswith('source_trace_core_route_'))]
    for e in records:
        if e['type'] in ['pcb_trace', 'pcb_via']:
            e['source_trace_id'] = bindings[e[e['type']+'_id']]
    return sorted(remove)


def add_power_fanouts(records):
    """Add real top traces and plated through vias for isolated supply branches."""
    geometry = Copper(records)
    power = next(e for e in records if e['type'] == 'source_net' and e['name'] == 'V3V3')
    key = power['subcircuit_connectivity_map_key']
    elements, roots = geometry.groups(key)
    obstacles = geometry.elements()
    foreign = [shapes for _, net, shapes in obstacles if net != key]
    all_tree = STRtree([shape for shapes in foreign for shape in shapes.values()])
    top_tree = STRtree([shapes['top'] for shapes in foreign if 'top' in shapes])
    added = []
    for root in sorted(set(roots)):
        members = [e for e, group in zip(elements, roots) if group == root]
        pads = [e for e in members if e[0]['type'] == 'pcb_smtpad']
        if not pads or any(e[0]['type'] == 'pcb_via' for e in members):
            continue
        choices = []
        for pad, _, _ in pads:
            for radius in [.5, .6, .7, .8, 1., 1.2, 1.5, 2.]:
                for angle in range(0, 360, 45):
                    x = round(pad['x'] + radius*math.cos(math.radians(angle)), 6)
                    y = round(pad['y'] + radius*math.sin(math.radians(angle)), 6)
                    via = Point(x, y).buffer(.225, quad_segs=32)
                    trace = LineString([(pad['x'], pad['y']), (x, y)]).buffer(.08, quad_segs=32)
                    if len(all_tree.query(via, predicate='dwithin', distance=.15-1e-8)) or len(
                            top_tree.query(trace, predicate='dwithin', distance=.15-1e-8)):
                        continue
                    choices.append((radius, pad, x, y))
        if not choices:
            raise RuntimeError('No safe supply fanout')
        _, pad, x, y = min(choices, key=lambda c: c[0])
        index = len(added)
        source_trace = next(e for e in records if e.get('source_trace_id') == 'source_trace_core_route_V3V3' and e['type'] == 'source_trace')
        common = {'source_net_id': power['source_net_id'], 'subcircuit_connectivity_map_key': key,
                  'source_trace_id': source_trace['source_trace_id']}
        records.append({'type': 'pcb_via', 'pcb_via_id': f'core_supply_fanout_{index}',
                        'x': x, 'y': y, 'hole_diameter': .30, 'outer_diameter': .45,
                        'layers': LAYERS, **common})
        records.append({'type': 'pcb_trace', 'pcb_trace_id': f'core_supply_fanout_{index}',
                        'pcb_port_ids': [pad['pcb_port_id']], **common,
                        'route': [{'route_type': 'wire', 'x': a, 'y': b, 'width': .16, 'layer': 'top'}
                                  for a, b in [(pad['x'], pad['y']), (x, y)]]})
        added.append({'pcb_port_id': pad['pcb_port_id'], 'via': [x, y]})
    return added


def fill_ground(records):
    geometry = Copper(records)
    ground = next(e for e in records if e['type'] == 'source_net' and e['name'] == 'GND')
    power = next(e for e in records if e['type'] == 'source_net' and e['name'] == 'V3V3')
    elements = geometry.elements()
    regions = []
    board = next(e for e in records if e['type'] == 'pcb_board')
    inset = .35
    boundary = box(-board['width']/2 + inset, -board['height']/2 + inset,
                   board['width']/2 - inset, board['height']/2 - inset)
    for layer in LAYERS:
        plane = power if layer == 'inner2' else ground
        key = plane['subcircuit_connectivity_map_key']
        obstacles, anchors = [], []
        for record, net, shapes in elements:
            if layer not in shapes:
                continue
            shape = shapes[layer]
            if net == key:
                anchors.append(shape)
            else:
                obstacles.append(shape.buffer(.20, quad_segs=16))
        area = boundary.difference(unary_union(obstacles))
        polygons = [area] if area.geom_type == 'Polygon' else list(area.geoms)
        for i, polygon in enumerate(polygons):
            if polygon.area < .02 or not any(polygon.intersects(a) for a in anchors):
                continue
            # Keep source precision and split any narrow islands created by rounding.
            points = lambda ring: [(round(x, 6), round(y, 6)) for x, y in list(ring.coords)[:-1]]
            exact = Polygon(points(polygon.exterior), [points(r) for r in polygon.interiors]).buffer(0)
            pieces = [exact] if exact.geom_type == 'Polygon' else list(exact.geoms)
            for k, piece in enumerate(pieces):
                if piece.area < .02 or not any(piece.intersects(a) for a in anchors):
                    continue
                piece = orient(piece, sign=-1)
                ring = lambda r: {'vertices': [{'x': x, 'y': y} for x, y in points(r)]}
                records.append({'type': 'pcb_copper_pour', 'pcb_copper_pour_id': f'core_ground_{layer}_{i}_{k}',
                                'source_net_id': plane['source_net_id'], 'subcircuit_connectivity_map_key': key,
                                'subcircuit_id': 'subcircuit_source_group_0', 'layer': layer, 'shape': 'brep',
                                'covered_with_solder_mask': True, 'brep_shape': {'outer_ring': ring(piece.exterior),
                                'inner_rings': [ring(r) for r in piece.interiors]}})
                regions.append({'layer': layer, 'net': plane['name'], 'area_mm2': piece.area})
    return regions


if __name__ == '__main__':
    base_path = ROOT / 'artifacts/rp2040-core/core.circuit.json'
    seed_path = ROOT / 'src/pcb/core-routing-seed.json'
    base, seed = json.loads(base_path.read_text()), json.loads(seed_path.read_text())
    records = build(base, seed)
    removed = prune_absent_branches(records)
    fanouts = add_power_fanouts(records)
    orphan_copper = bind_physical_route_groups(records)
    regions = fill_ground(records)
    OUT.mkdir(exist_ok=True)
    path = OUT / 'board.circuit.json'
    path.write_text(json.dumps(records, indent=2) + '\n')
    errors = Copper(records).connectivity()
    report = {'scope': 'MCU subsystem PCB development candidate; full controller incomplete',
              'board_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'source_sha256': hashlib.sha256(base_path.read_bytes()).hexdigest(),
              'routing_seed_sha256': hashlib.sha256(seed_path.read_bytes()).hexdigest(),
              'all_119_supplier_pad_poses_match_reference': True,
              'counts': dict(Counter(e['type'] for e in records if e['type'] in ['pcb_trace', 'pcb_via', 'pcb_copper_pour'])),
              'removed_absent_component_stubs': removed,
              'removed_copper_without_retained_pad': orphan_copper,
              'plane_regions': regions, 'added_supply_fanouts': fanouts, 'physical_connectivity_errors': errors,
              'mounting_holes_added': False, 'motor_geometry_invented': False,
              'manufacturing_release': False}
    (OUT / 'routing-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(errors))
