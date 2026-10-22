"""Verify native schematic pin geometry and source nets without changing output."""
from collections import Counter
import json
import math
from pathlib import Path

records = json.loads(Path('dist/index/circuit.json').read_text())
spec = json.loads(Path('config/connections.json').read_text())['components']
components = {x['source_component_id']: x for x in records if x['type'] == 'source_component'}
source_ports = {x['source_port_id']: x for x in records if x['type'] == 'source_port'}
nets = {x['source_net_id']: x for x in records if x['type'] == 'source_net'}
net_names = {x['name']: x for x in nets.values()}
traces = [x for x in records if x['type'] == 'schematic_trace']
labels = [x for x in records if x['type'] == 'schematic_net_label']
logical_traces = [x for x in records if x['type'] == 'source_trace']


def on_segment(point, a, b):
    dx, dy = b['x'] - a['x'], b['y'] - a['y']
    length2 = dx * dx + dy * dy
    if length2 < 1e-14:
        return math.hypot(point['x'] - a['x'], point['y'] - a['y']) < 1e-6
    t = ((point['x'] - a['x']) * dx + (point['y'] - a['y']) * dy) / length2
    return -1e-6 < t < 1 + 1e-6 and math.hypot(point['x'] - a['x'] - t * dx, point['y'] - a['y'] - t * dy) < 1e-6


failures, findings = [], []
counts = Counter()
for port in [x for x in records if x['type'] == 'schematic_port']:
    source = source_ports[port['source_port_id']]
    name = components[source['source_component_id']]['name']
    pin = str(source['pin_number'])
    physical = {'component': name, 'pin': pin, 'schematic_port_id': port['schematic_port_id']}
    linked = [t for t in logical_traces if source['source_port_id'] in t.get('connected_source_port_ids', [])]
    if pin in spec[name]['no_connect']:
        counts['explicit_no_connect_ports'] += 1
        if linked or port.get('is_connected'):
            failures.append({**physical, 'problem': 'Explicit NC has a connection'})
        continue
    expected = spec[name]['connections'].get(pin)
    if expected is None:
        failures.append({**physical, 'problem': 'Port absent from intended net and NC definitions'})
        continue
    key = net_names[expected]['subcircuit_connectivity_map_key']
    valid_source = source.get('subcircuit_connectivity_map_key') == key and any(net_names[expected]['source_net_id'] in t.get('connected_source_net_ids', []) for t in linked)
    matching_traces = [t['schematic_trace_id'] for t in traces if t.get('schematic_sheet_id') == port['schematic_sheet_id'] and t.get('subcircuit_connectivity_map_key') == key and any(on_segment(port['center'], edge['from'], edge['to']) for edge in t['edges'])]
    matching_labels = [label['schematic_net_label_id'] for label in labels if label.get('schematic_sheet_id') == port['schematic_sheet_id'] and nets.get(label.get('source_net_id'), {}).get('subcircuit_connectivity_map_key') == key and math.hypot(label['anchor_position']['x'] - port['center']['x'], label['anchor_position']['y'] - port['center']['y']) < 1e-6]
    if not valid_source or not (matching_traces or matching_labels):
        failures.append({**physical, 'expected_net': expected, 'source_net_valid': valid_source, 'matching_traces': matching_traces, 'matching_labels': matching_labels})
    else:
        counts['geometry_and_source_connected_ports'] += 1
        if not port.get('is_connected'):
            findings.append({**physical, 'expected_net': expected, 'reported_is_connected': port.get('is_connected'), 'matching_traces': matching_traces, 'matching_labels': matching_labels})
report = {'counts': dict(counts), 'total_schematic_ports': sum(x['type'] == 'schematic_port' for x in records), 'source_and_schematic_geometry_passed': not failures, 'failures': failures, 'is_connected_metadata_discrepancy_count': len(findings), 'metadata_discrepancies': findings, 'schematic_layout_approved': False, 'schematic_shorts_approved': False, 'pcb_connectivity_approved': False, 'scope': 'Every non-NC pin must have its intended source net plus same-net wire geometry or an anchored net label; the native is_connected flag alone is not used as proof.'}
Path('checks/20261023/schematic-port-connectivity.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: v for k, v in report.items() if k != 'metadata_discrepancies'}, indent=2))
raise SystemExit(bool(failures))
