#!/usr/bin/env python3
"""Verify exact native CLI roundtrip and committed provenance of routed prototype."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'prototypes/controller-pcb-0.3.0'
records=json.loads((p/'index.circuit.json').read_text())
assert json.loads((p/'dist/index/circuit.json').read_text())==records
proof=json.loads((p/'package-verification.json').read_text())
historical=subprocess.check_output(['git','show',proof['source_milestone_commit']+':'+proof['source_path']],cwd=ROOT)
assert json.loads(historical)==records
assert proof['circuit_sha256']==hashlib.sha256((p/'index.circuit.json').read_bytes()).hexdigest()
seen=set()
for e in records:
    identity=(e['type'],e[e['type']+'_id'])
    assert identity not in seen,identity
    seen.add(identity)
for kind,count in [('source_component',94),('source_port',341),('schematic_sheet',6),('cad_component',84),('pcb_trace',554),('pcb_via',334)]:
    assert sum(e['type']==kind for e in records)==count
assert not proof['manufacturing_release']
proof.update(native_CLI_record_roundtrip_equal=True,unique_native_record_ids=True)
(p/'package-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
print('Native routed prototype exact CLI roundtrip, historical provenance and unique IDs PASS')
