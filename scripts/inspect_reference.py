#!/usr/bin/env python3
"""Inventory a read-only reference copy without treating it as a qualified baseline."""
import argparse
import hashlib
import json
from pathlib import Path


def inspect(root, commit):
    native = root / 'index.circuit.json'
    records = json.loads(native.read_text())
    metadata = json.loads((root / 'package.json').read_text())
    source = {x['source_component_id']: x for x in records
              if x['type'] == 'source_component'}
    ports = [x for x in records if x['type'] == 'source_port']
    nets = {x['subcircuit_connectivity_map_key']: x['name'] for x in records
            if x['type'] == 'source_net'}
    pcb = {x['source_component_id']: x for x in records
           if x['type'] == 'pcb_component' and x.get('source_component_id')}
    components = []
    for identifier, s in source.items():
        p = [{'pin': x.get('pin_number'), 'name': x.get('name'),
              'net': nets.get(x.get('subcircuit_connectivity_map_key'))}
             for x in ports if x['source_component_id'] == identifier]
        land = pcb.get(identifier)
        components.append({
            'reference': s['name'],
            'manufacturer_part_number': s.get('manufacturer_part_number'),
            'supplier_part_numbers': s.get('supplier_part_numbers'),
            'resistance_ohms': s.get('resistance'),
            'capacitance_f': s.get('capacitance'),
            'pcb_assembly': {'layer': land.get('layer'),
                             'do_not_place': bool(land.get('do_not_place'))}
                            if land else None,
            'pins': p
        })
    return {
        'status': 'inspection_only_published_identity_not_verified',
        'requested_version': '1.13.0',
        'observed_github_version': metadata['version'],
        'repository': 'AnasSarkiz/NEMA14_RP2040',
        'branch': 'fix/nema14-ai-review-20261013',
        'commit': commit,
        'board_sha256': hashlib.sha256(native.read_bytes()).hexdigest(),
        'source_sha256': hashlib.sha256((root / 'src/board.tsx').read_bytes()).hexdigest(),
        'components': components
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--commit', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = inspect(args.root, args.commit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2) + '\n')
