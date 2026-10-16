#!/usr/bin/env python3
"""Check native symbol pins, real net stubs and labels against electrical source."""
import hashlib
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


def same(a, b):
    return math.hypot(a['x'] - b['x'], a['y'] - b['y']) < 1e-7


def validate(base, records):
    errors = []
    if records[:len(base)] != base:
        errors.append('Electrical / PCB / CAD records changed during presentation')
    source = {e['source_port_id']: e for e in base if e['type'] == 'source_port'}
    nets = {e['subcircuit_connectivity_map_key']: e for e in base if e['type'] == 'source_net'}
    traces = [e for e in records if e['type'] == 'schematic_trace']
    labels = [e for e in records if e['type'] == 'schematic_net_label']
    symbols = [e for e in records if e['type'] == 'schematic_port']
    if len(symbols) != len(source):
        errors.append('Symbol port count differs from physical source port count')
    for identifier, port in source.items():
        matches = [e for e in symbols if e['source_port_id'] == identifier]
        if len(matches) != 1:
            errors.append('Physical pin does not have exactly one symbol port: ' + identifier)
            continue
        symbol = matches[0]
        key = port.get('subcircuit_connectivity_map_key')
        attached = [(t, edge) for t in traces for edge in t['edges']
                    if edge.get('from_schematic_port_id') == symbol['schematic_port_id']]
        if not key:
            if attached or symbol.get('is_connected'):
                errors.append('Intentionally unused pin is falsely connected: ' + identifier)
            continue
        if len(attached) != 1:
            errors.append('Connected pin must have exactly one labelled wire stub: ' + identifier)
            continue
        trace, edge = attached[0]
        if trace.get('subcircuit_connectivity_map_key') != key:
            errors.append('Wire stub has wrong electrical net: ' + identifier)
        if not same(symbol['center'], edge['from']):
            errors.append('Wire does not touch symbol pin: ' + identifier)
        if same(edge['from'], edge['to']):
            errors.append('Wire stub has zero length: ' + identifier)
        net = nets[key]
        matches = [l for l in labels if l['schematic_sheet_id'] == symbol['schematic_sheet_id']
                   and same(l['anchor_position'], edge['to'])
                   and l.get('subcircuit_connectivity_map_key') == key
                   and l.get('source_net_id') == net['source_net_id'] and l['text'] == net['name']]
        if len(matches) != 1:
            errors.append('Wire endpoint has no unique correct net label: ' + identifier)
    if len([e for e in records if e['type'] == 'schematic_sheet']) != 3:
        errors.append('Expected three functional A4 sheets')
    return errors


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1] / 'artifacts/rp2040-core'
    base = json.loads((root / 'core.circuit.json').read_text())
    path = root / 'core-schematic.circuit.json'
    errors = validate(base, json.loads(path.read_text()))
    native_path = root / 'native-schematic-placement.txt'
    if not native_path.exists():
        errors.append('Native schematic placement log missing')
        issue_count = None
    else:
        xml = ET.fromstring('<analysis>' + native_path.read_text() + '</analysis>')
        issue_count = sum(len(e) for e in xml.iter('SchematicPlacementIssues'))
        if issue_count:
            errors.append(f'Native schematic placement reports {issue_count} issues')
    report = {'scope': 'MCU subsystem symbol connectivity and schematic geometry; not full-controller ERC',
              'passed': not errors, 'errors': errors, 'physical_ports_checked': 119,
              'native_placement_issues': issue_count,
              'schematic_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'base_sha256': hashlib.sha256((root / 'core.circuit.json').read_bytes()).hexdigest(),
              'manufacturing_release': False}
    (root / 'schematic-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    sys.exit(bool(errors))
