#!/usr/bin/env python3
"""Reproduce the native compact six-layer routing checkpoint from checked source."""
import argparse,hashlib,json
from pathlib import Path
from fill_controller_ground import fill
from prepare_controller_stencil import prepare
from annotate_compact_pcb import annotate

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
folder=ROOT/'artifacts/compact-six-layer';source=folder/'unrouted.circuit.json';routing=ROOT/'src/compact/six-layer-routing.json'
construction=json.loads(routing.read_text());assert construction['unrouted_source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
records=json.loads(source.read_text());assert next(e for e in records if e['type']=='pcb_board')['num_layers']==6
records.extend(construction['records']);prepare(records);fill(records);silk=annotate(records)
data=(json.dumps(records,indent=2)+'\n').encode();path=folder/'board.circuit.json'
if a.check:
    if path.read_bytes()!=data:raise ValueError('Compact six-layer source does not reproduce the checked board')
else:path.write_bytes(data)
inputs=['artifacts/compact-six-layer/unrouted.circuit.json','src/compact/six-layer-routing.json','config/compact-routing-placement.json','config/compact-four-mount-routing-constraints.json','config/controller-silkscreen-font.json','scripts/build_compact_six_layer.py','scripts/fill_controller_ground.py','scripts/prepare_controller_stencil.py','scripts/annotate_compact_pcb.py']
report=dict(scope='Native tscircuit six-layer copper checkpoint; USB, hardware and manufacturing qualification remain separate',circuit_sha256=hashlib.sha256(data).hexdigest(),inputs=[dict(path=f,sha256=hashlib.sha256((ROOT/f).read_bytes()).hexdigest()) for f in inputs],manufacturing_release=False)
(folder/'PCB-build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(native_PCB_reproduces=True,circuit_sha256=report['circuit_sha256'],manufacturing_release=False)))
