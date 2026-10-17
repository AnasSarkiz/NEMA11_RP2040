#!/usr/bin/env python3
"""Reviewed route edits; never exceptions to the final physical audits."""
import json
from pathlib import Path
from pcb_geometry import Copper

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/controller-pcb'


def refine(records):
    # This inherited signal barrel would sit in the moved resistor pad. Remove
    # it and construct a fresh physical connection with the ordinary router.
    identifier = 'controller_reviewed_local_R_STATUS_B_pin1_via'
    obsolete = set(json.loads((ROOT / 'src/controller/remove-obsolete-stubs.json').read_text()))
    records[:] = [e for e in records if e.get('pcb_via_id') != identifier
                  and e.get('pcb_trace_id') not in obsolete
                  and not e.get('pcb_trace_id', '').startswith('controller_RGB_via_relocation_')]
    trace = next(e for e in records if e.get('pcb_trace_id') == 'controller_same_side_repair_15_DATA_VBUS_1_layer_section_0')
    # The new diode branch joins this run at Y=14.3; remove only the old
    # connector-side leaf beyond that junction, retaining positive overlap.
    assert trace['route'][0]['x'] == 8.125
    trace['route'][0]['y'] = 14.4
    for e in records:
        if e['type'] == 'source_trace' and e['source_trace_id'] == 'source_trace_controller_route_GND':
            e['connected_source_port_ids'] = []
    journal = ROOT / 'src/controller/trimmed-route-leaves.json'
    if journal.exists():
        edits = json.loads(journal.read_text())
        for edit in edits:
            route = next((e for e in records if e.get('pcb_trace_id') == edit['id']), None)
            if route is not None:
                if edit['route'] is None:
                    records.remove(route)
                else:
                    route['route'] = edit['route']
    # Match each return run to an actual retained pad in its copper group.
    # Original pin-to-net source traces still describe every ground connection.
    copper = Copper(records)
    ground = next(k for k, n in copper.nets.items() if n == 'GND')
    elements, roots = copper.groups(ground)
    by_port = {e['connected_source_port_ids'][0]: e['source_trace_id'] for e in records
               if e['type'] == 'source_trace' and len(e['connected_source_port_ids']) == 1}
    pads = {}
    for (e, _, _), group in zip(elements, roots):
        if e['type'] in ['pcb_smtpad', 'pcb_plated_hole']:
            pads.setdefault(group, []).append(e)
    identities = {}
    for (e, _, _), group in zip(elements, roots):
        if e['type'] == 'pcb_trace' and group in pads:
            pad = min(pads[group], key=lambda p: min((p['x']-q['x'])**2 + (p['y']-q['y'])**2 for q in e['route']))
            identities[e['pcb_trace_id']] = by_port[copper.ports[pad['pcb_port_id']]['source_port_id']]
    for e in records:
        if e['type'] == 'pcb_trace' and e['pcb_trace_id'] in identities:
            e['source_trace_id'] = identities[e['pcb_trace_id']]


if __name__ == '__main__':
    path = OUT / 'board.circuit.json'
    records = [e for e in json.loads(path.read_text()) if e['type'] != 'pcb_copper_pour']
    refine(records)
    path.write_text(json.dumps(records, indent=2) + '\n')
    (OUT / 'reviewed-route-edits.json').write_text(json.dumps({
        'scope': 'Physical routing edits requiring subsequent independent DRC',
        'removed_signal_via': 'controller_reviewed_local_R_STATUS_B_pin1_via',
        'reason': 'Remove barrel from moved R_STATUS_B pad and construct a new connection',
        'manufacturing_release': False}, indent=2) + '\n')
