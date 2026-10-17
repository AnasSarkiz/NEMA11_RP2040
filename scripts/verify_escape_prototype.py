#!/usr/bin/env python3
"""Verify every native prototype record against the committed checkpoint."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'prototypes/compact-escape-0.2.0'
proof=json.loads((folder/'package-verification.json').read_text());data=(folder/'index.circuit.json').read_bytes()
assert hashlib.sha256(data).hexdigest()==proof['circuit_sha256']
original=json.loads(subprocess.check_output(['git','show',proof['source_milestone_commit']+':artifacts/compact-escape/assembly.circuit.json'],cwd=ROOT))
records=json.loads(data);assert records==original
assert json.loads((folder/'dist/index/circuit.json').read_text())==records
assert sum(e['type']=='source_component' for e in records)==94 and sum(e['type']=='source_port' for e in records)==340
assert sum(e['type']=='cad_component' and not next((p.get('do_not_place') for p in records if p['type']=='pcb_component' and p['pcb_component_id']==e.get('pcb_component_id')),False) for e in records)==84
assert not proof['manufacturing_release'] and not proof['full_controller_routing_complete'] and proof['disconnected_controller_nets']==58
print('Compact escape 0.2.0: committed native assembly and every CLI roundtrip record verified; 58 nets explicitly open')
