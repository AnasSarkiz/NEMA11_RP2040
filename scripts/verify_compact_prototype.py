#!/usr/bin/env python3
"""Verify the immutable native compact prototype independently of later layouts."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'prototypes/compact-placement-0.1.0';p=json.loads((folder/'package-verification.json').read_text());data=(folder/'index.circuit.json').read_bytes();records=json.loads(data)
assert hashlib.sha256(data).hexdigest()==p['circuit_sha256']
assert json.loads((folder/'dist/index/circuit.json').read_text())==records
original=json.loads(subprocess.check_output(['git','show',p['source_milestone_commit']+':artifacts/compact-controller/assembly.circuit.json'],cwd=ROOT))
assert original==records
assert sum(e['type']=='source_component' for e in records)==94
assert sum(e['type']=='source_port' for e in records)==340
assert sum(e['type']=='source_net' for e in records)==64
assert sum(e['type']=='schematic_sheet' for e in records)==6
assert sum(e['type']=='cad_component' for e in records)==87 # 82 fitted + 3 encoder DNP + motor/carrier
assert not any(e['type']=='pcb_trace' for e in records)
assert not p['manufacturing_release'] and not p['physical_routing_complete']
print('Immutable compact prototype: exact committed assembly and every native CLI roundtrip record verified')
