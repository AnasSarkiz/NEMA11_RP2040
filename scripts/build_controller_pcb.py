#!/usr/bin/env python3
"""Reproduce the fixed native routing milestone from TSX output and native copper source."""
import argparse
import hashlib
import json
from pathlib import Path
from route_controller_pcb import build
from refine_controller_routing import refine
from fill_controller_ground import fill
from annotate_controller_pcb import annotate

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
source = ROOT / 'artifacts/controller/unrouted.circuit.json'
connections = json.loads((ROOT / 'src/controller/constructed-connections.json').read_text())
assert connections['unrouted_source_sha256'] == hashlib.sha256(source.read_bytes()).hexdigest()
records, _ = build(json.loads(source.read_text()), json.loads((ROOT / 'src/controller/reference-routing-seed.json').read_text()))
refine(records)
records.extend(connections['records'])
refine(records)
fill(records)
annotate(records)
output = (json.dumps(records,indent=2)+'\n').encode()
path = ROOT / 'artifacts/controller-pcb/board.circuit.json'
if args.check:
    assert path.read_bytes() == output, 'Native routing source does not reproduce the checked board'
else:
    path.write_bytes(output)
print(json.dumps({'native_PCB_reproduces':True,'circuit_sha256':hashlib.sha256(output).hexdigest()}))
