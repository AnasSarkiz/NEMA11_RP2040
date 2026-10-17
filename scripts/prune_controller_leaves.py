#!/usr/bin/env python3
"""Review native dangling branches; require unchanged physical pad connectivity."""
import hashlib
import json
from pathlib import Path
from shapely.geometry import LineString, Point
from shapely.ops import unary_union, substring
from pcb_geometry import Copper

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'artifacts/controller-pcb/board.circuit.json'
diagnostics = json.loads((path.parent / 'native-drc.json').read_text())
assert diagnostics['circuit_sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
records = [e for e in json.loads(path.read_text()) if e['type'] != 'pcb_copper_pour']
journal_path = ROOT / 'src/controller/trimmed-route-leaves.json'
journal = {e['id']: e for e in json.loads(journal_path.read_text())}
errors = [e for e in diagnostics['errors'] if 'dangling endpoint' in e.get('message', '')]


def count(candidate, key):
    members, roots = Copper(candidate).groups(key)
    return len({root for (e, _, _), root in zip(members, roots)
                if e['type'] in ['pcb_smtpad', 'pcb_plated_hole']})


for identifier in sorted({e['pcb_trace_id'] for e in errors}):
    trace = next(e for e in records if e.get('pcb_trace_id') == identifier)
    key = trace['subcircuit_connectivity_map_key']
    before = count(records, key)
    candidate = [e for e in records if e is not trace]
    if count(candidate, key) == before:
        records = candidate
        route = None
    else:
        for error in [e for e in errors if e['pcb_trace_id'] == identifier]:
            coords = [(p['x'], p['y']) for p in trace['route']]
            reverse = error['pcb_trace_error_id'].endswith('_end')
            line = LineString(coords[::-1] if reverse else coords)
            copper = Copper(candidate)
            # An unused old barrel is not the destination for a retained leaf.
            # Trim to another physical pad or trace; preserve true layer-change
            # junctions through the unchanged pad-island check below.
            rest = unary_union([s for e, net, shapes in copper.elements() if net == key and e['type'] != 'pcb_via'
                                for layer, s in shapes.items() if layer == trace['route'][0]['layer']])
            points = []

            def visit(g):
                if hasattr(g, 'geoms'):
                    for child in g.geoms:
                        visit(child)
                elif hasattr(g, 'coords'):
                    points.extend(list(g.coords))

            visit(line.intersection(rest))
            distance = min(line.project(Point(p)) for p in points)
            new = list(substring(line, min(distance + .04, line.length - .01), line.length).coords)
            new = new[::-1] if reverse else new
            prototype = trace['route'][0]
            trace['route'] = [{'route_type': 'wire', 'x': x, 'y': y,
                               'width': prototype['width'], 'layer': prototype['layer']} for x, y in new]
        assert count(records, key) == before
        route = trace['route']
    journal[identifier] = {'id': identifier, 'route': route, 'physical_pad_islands_before_after': [before, before]}
path.write_text(json.dumps(records, indent=2) + '\n')
journal_path.write_text(json.dumps(list(journal.values()), indent=2) + '\n')
print(json.dumps({'dangling_trace_ids_reviewed': len({e['pcb_trace_id'] for e in errors})}))
