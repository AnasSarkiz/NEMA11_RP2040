#!/usr/bin/env python3
"""Verify every routed package record against committed source and the real CLI."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];F=ROOT/'prototypes/compact-six-layer-0.4.0';proof=json.loads((F/'package-verification.json').read_text());data=(F/'index.circuit.json').read_bytes();assert hashlib.sha256(data).hexdigest()==proof['circuit_sha256'];records=json.loads(data)
original=json.loads(subprocess.check_output(['git','show',proof['source_milestone_commit']+':artifacts/compact-six-layer/assembly.circuit.json'],cwd=ROOT));assert records==original and json.loads((F/'dist/index/circuit.json').read_text())==records
assert next(e for e in records if e['type']=='pcb_board')['num_layers']==6
assert sum(e['type']=='source_component' for e in records)==88 and sum(e['type']=='source_port' for e in records)==326
assert sum(e['type']=='pcb_hole' and not e.get('pcb_component_id') for e in records)==4
assert proof['native_copper_review_pass'] and proof['native_DRC_errors']==proof['physical_opens']==proof['physical_shorts']==0 and not proof['manufacturing_release']
print('Prototype 0.4.0: all six-layer routed records match committed source and actual CLI roundtrip; manufacturing qualification incomplete')
