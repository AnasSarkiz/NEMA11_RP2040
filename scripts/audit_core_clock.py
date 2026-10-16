#!/usr/bin/env python3
"""Clock copper and return-path checks; bench clock qualification is separate."""
import hashlib, json, math
from pathlib import Path
from shapely.geometry import Point, LineString
from shapely.ops import unary_union
from pcb_geometry import Copper

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'artifacts/rp2040-pcb/board.circuit.json'
records = json.loads(path.read_text())
c = Copper(records)
keys = {name: key for key, name in c.nets.items()}
errors, rows = [], []
for name, limit in {'XIN': 5, 'XOUT': 6, 'XTAL_OUT': 5}.items():
    traces = [e for e in records if e['type'] == 'pcb_trace' and c.key(e) == keys[name]]
    vias = [e for e in records if e['type'] == 'pcb_via' and c.key(e) == keys[name]]
    length, layers = 0., set()
    for trace in traces:
        for a, b in zip(trace['route'], trace['route'][1:]):
            if a['route_type'] == b['route_type'] == 'wire' and a['layer'] == b['layer']:
                length += math.dist((a['x'], a['y']), (b['x'], b['y']))
                layers.add(a['layer'])
    row = {'net': name, 'total_copper_mm': length, 'budget_mm': limit, 'layers': sorted(layers), 'signal_vias': len(vias)}
    rows.append(row)
    if not traces or vias or layers != {'top'} or length > limit:
        errors.append({'clock_route': row})
plan = json.loads((ROOT / 'src/pcb/oscillator-reservation.json').read_text())
region = unary_union([LineString(r['points']).buffer(plan['guard_buffer_mm']) for r in plan['routes']])
exemptions = unary_union([Point(r['points'][0]).buffer(plan['MCU_pin_local_exemption_radius_mm'])
                         for r in plan['routes'] if r['trace'] in ['oscillator_XIN', 'oscillator_XOUT']])
region = region.difference(exemptions)
for record, key, shapes in c.elements():
    if c.nets.get(key) in ['GND', 'XIN', 'XOUT', 'XTAL_OUT']:
        continue
    if any(shapes[layer].intersects(region) for layer in plan['layers_reserved'] if layer in shapes):
        errors.append({'reserved_clock_region': record[record['type']+'_id']})
ground_shapes = [shapes['inner1'] for record, key, shapes in c.elements()
                 if record['type'] == 'pcb_copper_pour' and key == keys['GND'] and 'inner1' in shapes]
plane = unary_union(ground_shapes)
returns = []
for name, pin in [('Y_MCU', 2), ('Y_MCU', 4), ('C_XIN', 2), ('C_XOUT', 2)]:
    port = next(p for p in c.ports.values() if c.names[c.source[p['source_port_id']]['source_component_id']] == name
                and c.source[p['source_port_id']]['pin_number'] == pin)
    vias = [e for e in records if e['type'] == 'pcb_via' and c.key(e) == keys['GND']
            and math.dist((port['x'], port['y']), (e['x'], e['y'])) <= 1.2
            and plane.intersects(Point(e['x'], e['y']).buffer(e['outer_diameter']/2))]
    returns.append({'pin': f'{name}.{pin}', 'ground_return_vias_within_1_2mm': len(vias)})
    if not vias:
        errors.append({'missing_clock_ground_return': f'{name}.{pin}'})
report = {'circuit_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'routes': rows,
          'ground_returns': returns, 'errors': errors, 'bench_startup_drive_load_frequency_verified': False,
          'manufacturing_release': False}
(ROOT/'artifacts/rp2040-pcb/clock-layout-audit.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report))
raise SystemExit(bool(errors))
