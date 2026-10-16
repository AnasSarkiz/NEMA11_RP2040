#!/usr/bin/env python3
"""Verify the separately built native prototype and its publication receipt."""
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'prototypes/rp2040-core'
source=PACKAGE/'index.circuit.json'
saved=json.loads(source.read_text())
built=json.loads((PACKAGE/'dist/index/circuit.json').read_text())
assert built==saved,'Native CLI changed saved PCB/schematic/CAD records'
seen=set()
for record in saved:
    identifier=(record['type'],record[record['type']+'_id'])
    assert identifier not in seen,identifier
    seen.add(identifier)
board=json.loads((ROOT/'artifacts/rp2040-pcb/board.circuit.json').read_text())
assert saved[:len(board)]==board
assert sum(e['type']=='schematic_sheet' for e in saved)==3
proof=json.loads((PACKAGE/'package-verification.json').read_text())
assert proof['circuit_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
assert proof['registry_published'] is False and proof['manufacturing_release'] is False
proof.update(native_CLI_record_roundtrip_equal=True,unique_native_record_ids=True)
(PACKAGE/'package-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
print('Separate prototype: exact native CLI roundtrip, unique IDs and PCB/schematic preservation PASS')
