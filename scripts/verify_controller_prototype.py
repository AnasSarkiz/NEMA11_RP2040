#!/usr/bin/env python3
"""Require exact native CLI roundtrip before publishing the source prototype."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
package = ROOT / 'prototypes/full-controller'
source = package / 'index.circuit.json'
records = json.loads(source.read_text())
assert json.loads((package / 'dist/index/circuit.json').read_text()) == records
assert json.loads((ROOT / 'artifacts/controller/schematic.circuit.json').read_text()) == records
seen = set()
for e in records:
    identity = (e['type'], e[e['type'] + '_id'])
    assert identity not in seen, identity
    seen.add(identity)
assert sum(e['type'] == 'schematic_sheet' for e in records) == 6
assert sum(e['type'] == 'source_component' for e in records) == 92
assert sum(e['type'] == 'source_port' for e in records) == 341
proof = json.loads((package / 'package-verification.json').read_text())
assert proof['circuit_sha256'] == hashlib.sha256(source.read_bytes()).hexdigest()
assert proof['manufacturing_release'] is False
proof.update(native_CLI_record_roundtrip_equal=True, unique_native_record_ids=True)
(package / 'package-verification.json').write_text(json.dumps(proof, indent=2) + '\n')
print('Controller prototype: exact native CLI roundtrip and unique record IDs PASS')
