#!/usr/bin/env python3
"""Transfer unchanged exact-reference corridors for independently checked rerouting."""
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from pcb_geometry import pad_shape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/controller-pcb'
MOVED = {'J_PD', 'J_MOTOR', 'D_DATA', 'R_STATUS_B'}


def build(base, seed):
    result = copy.deepcopy(base)
    sources = {e['source_component_id']: e['name'] for e in base if e['type'] == 'source_component'}
    sp = {e['source_port_id']: e for e in base if e['type'] == 'source_port'}
    pp = {e['pcb_port_id']: e for e in base if e['type'] == 'pcb_port'}
    ports = {(sources[sp[p['source_port_id']]['source_component_id']], sp[p['source_port_id']]['pin_number']): p for p in pp.values()}
    pads = {}
    for p in base:
        if p['type'] not in ['pcb_smtpad', 'pcb_plated_hole']:
            continue
        s = sp[pp[p['pcb_port_id']]['source_port_id']]
        pads.setdefault((sources[s['source_component_id']], s['pin_number']), []).append(p)
    checked = 0
    for old in seed['physical_pads']:
        name, pin = old['component'], old['pin']
        if name in MOVED:
            continue
        candidates = pads.get((name, pin), [])
        assert any(p['type'] == old['pad']['type'] and pad_shape(p).hausdorff_distance(pad_shape(old['pad'])) < .001
                   for p in candidates), (name, pin, 'Reference land pattern/pose changed')
        checked += 1
    nets = {e['name']: e for e in base if e['type'] == 'source_net'}
    trace_ids = {}
    for name, net in nets.items():
        identifier = 'source_trace_controller_route_' + name
        trace_ids[name] = identifier
        result.append({'type':'source_trace', 'source_trace_id':identifier,
                       # Plane returns retain their original pin-to-net source
                       # traces. The construction trace describes ground copper.
                       'connected_source_port_ids':[] if name == 'GND' else [p['source_port_id'] for p in sp.values()
                                                    if p.get('subcircuit_connectivity_map_key') == net['subcircuit_connectivity_map_key']],
                       'connected_source_net_ids':[net['source_net_id']],
                       'subcircuit_connectivity_map_key':net['subcircuit_connectivity_map_key'],
                       'subcircuit_id':net['subcircuit_id']})
    remap = {identifier: ports[(p['component'], p['pin'])]['pcb_port_id']
             for identifier, p in seed['port_by_id'].items()
             if p['component'] not in MOVED and (p['component'],p['pin']) in ports}
    for raw in seed['routing']:
        name = seed['net_by_key'][raw['subcircuit_connectivity_map_key']]
        e = copy.deepcopy(raw)
        net = nets[name]
        e['source_net_id'] = net['source_net_id']
        e['source_trace_id'] = trace_ids[name]
        e['subcircuit_connectivity_map_key'] = net['subcircuit_connectivity_map_key']
        e[e['type'] + '_id'] = 'controller_' + e[e['type'] + '_id']
        if e['type'] == 'pcb_trace':
            e['pcb_port_ids'] = [remap[p] for p in e.get('pcb_port_ids', []) if p in remap]
            for point in e['route']:
                for field in ['start_pcb_port_id','end_pcb_port_id']:
                    old = point.pop(field, None)
                    if old in remap:
                        point[field] = remap[old]
        result.append(e)
    return result, {'unchanged_reference_pads_verified':checked,
                    'moved_components':sorted(MOVED), 'nets_removed_for_rerouting':[],
                    'removed_reference_copper_ids':[]}


if __name__ == '__main__':
    path = ROOT / 'artifacts/controller/unrouted.circuit.json'
    seed_path = ROOT / 'src/controller/reference-routing-seed.json'
    records, report = build(json.loads(path.read_text()), json.loads(seed_path.read_text()))
    OUT.mkdir(exist_ok=True)
    output = OUT / 'seeded.circuit.json'
    output.write_text(json.dumps(records, indent=2) + '\n')
    report.update(scope='Routing construction intermediate; opens, clearance and planes unresolved',
                  source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  circuit_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                  copper_counts=dict(Counter(e['type'] for e in records if e['type'] in ['pcb_trace','pcb_via'])),
                  reference_seed_sha256=hashlib.sha256(seed_path.read_bytes()).hexdigest(),
                  manufacturing_release=False)
    (OUT / 'seed-transfer.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'removed_reference_copper_ids'}))
