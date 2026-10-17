#!/usr/bin/env python3
"""Check the immutable native four-hole package and real CLI JSON roundtrip."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'prototypes/compact-four-mounts-0.3.0'
proof=json.loads((folder/'package-verification.json').read_text());data=(folder/'index.circuit.json').read_bytes()
assert hashlib.sha256(data).hexdigest()==proof['circuit_sha256']
records=json.loads(data)
original=json.loads(subprocess.check_output(['git','show',proof['source_milestone_commit']+':artifacts/compact-four-mounts/assembly.circuit.json'],cwd=ROOT))
assert records==original and json.loads((folder/'dist/index/circuit.json').read_text())==records
assert sum(e['type']=='source_component' for e in records)==88 and sum(e['type']=='source_port' for e in records)==326
assert sum(e['type']=='pcb_trace' for e in records)==0
assert sum(e['type']=='pcb_hole' and not e.get('pcb_component_id') for e in records)==4
assert sum(e['type']=='cad_component' and not next((p.get('do_not_place') for p in records if p['type']=='pcb_component' and p['pcb_component_id']==e.get('pcb_component_id')),False) for e in records)==78
assert not proof['manufacturing_release'] and not proof['full_controller_routing_complete'] and proof['disconnected_controller_nets']==61
print('Four-mount prototype 0.3.0: committed source, four holes, 78 models and every native CLI roundtrip record verified; UNROUTED')
