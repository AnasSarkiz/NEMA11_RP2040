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
from prepare_controller_stencil import prepare

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
prepare(records)
fill(records)
annotate(records)
output = (json.dumps(records,indent=2)+'\n').encode()
path = ROOT / 'artifacts/controller-pcb/board.circuit.json'
if args.check:
    assert path.read_bytes() == output, 'Native routing source does not reproduce the checked board'
else:
    path.write_bytes(output)
inputs=['artifacts/controller/unrouted.circuit.json','src/controller/reference-routing-seed.json',
        'src/controller/constructed-connections.json','src/controller/USB-locator-route-replacement.json',
        'src/controller/remove-obsolete-stubs.json','src/controller/trimmed-route-leaves.json',
        'src/controller/remove-orphan-copper.json','config/controller-silkscreen-font.json',
        'scripts/route_controller_pcb.py','scripts/refine_controller_routing.py',
        'scripts/fill_controller_ground.py','scripts/annotate_controller_pcb.py','scripts/prepare_controller_stencil.py']
manifest={'scope':'Native controller PCB reproduced from checked TSX output, exact reference copper and fixed native routing',
          'circuit_sha256':hashlib.sha256(output).hexdigest(),
          'inputs':[{'path':p,'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest()} for p in inputs],
          'manufacturing_release':False}
(path.parent/'PCB-build.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'native_PCB_reproduces':True,'circuit_sha256':hashlib.sha256(output).hexdigest()}))
