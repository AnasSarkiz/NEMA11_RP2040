#!/usr/bin/env python3
"""Reuse the checked routing with an explicit, separately checked bulk upgrade.

No previous source, routed board or prototype is rewritten. Construction is
not validation: run native DRC, independent copper/connectivity and CAM again.
"""
import argparse,hashlib,json
from pathlib import Path
from fill_controller_ground import fill
from prepare_controller_stencil import prepare
import annotate_compact_pcb as legends

ROOT=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--folder',type=Path,required=True);a=p.parse_args();f=a.folder.resolve();source=f/'unrouted.circuit.json';raw=source.read_bytes();new=json.loads(raw);old_path=ROOT/'artifacts/compact-six-layer/unrouted.circuit.json';old=json.loads(old_path.read_text())
if f in [ROOT/'artifacts/compact-six-layer',ROOT/'artifacts/compact-four-mounts',ROOT/'artifacts/compact-controller']:raise ValueError('Do not rewrite a frozen milestone')
def named(records):return {e['name']:e for e in records if e['type']=='source_component'}
old_components=named(old);new_components=named(new);assert set(old_components)==set(new_components)
for name in old_components:
    if name!='C_BULK':assert old_components[name]==new_components[name],name
bulk=new_components['C_BULK'];assert bulk['manufacturer_part_number']=='EEHZC1V680XP' and bulk['supplier_part_numbers']['jlcpcb']==['C178649'] and bulk['capacitance']==68e-6 and bulk['max_voltage_rating']==35
for typ in ['source_port','source_net','source_trace']:
    assert [e for e in old if e['type']==typ]==[e for e in new if e['type']==typ],typ+' identity or intent changed'
old_ports={e['pcb_port_id']:e for e in old if e['type']=='pcb_port'}
bulk_source_ports={e['source_port_id'] for e in new if e['type']=='source_port' and e['source_component_id']==bulk['source_component_id']}
for port in [e for e in new if e['type']=='pcb_port']:
    original=old_ports[port['pcb_port_id']]
    if port['source_port_id'] in bulk_source_ports:
        assert {k:v for k,v in port.items() if k not in ['x','y']}=={k:v for k,v in original.items() if k not in ['x','y']}
        assert max(abs(port[k]-original[k]) for k in ['x','y'])<.0002,'Unexpected bulk supplier-coordinate change'
    else:assert original==port,'Unchanged part moved'
board=next(e for e in new if e['type']=='pcb_board');assert board['num_layers']==6 and board['is_via_in_pad_allowed'] is True
route_path=ROOT/'src/compact/six-layer-routing.json';routing=json.loads(route_path.read_text());assert routing['unrouted_source_sha256']==hashlib.sha256(old_path.read_bytes()).hexdigest()
records=new+routing['records'];prepare(records);fill(records)
legends.LABELS=[(text.replace('PROTOTYPE 0.4','HYBRID DEV'),x,y,size) for text,x,y,size in legends.LABELS];annotation=legends.annotate(records);output=(json.dumps(records,indent=2)+'\n').encode();(f/'board.circuit.json').write_bytes(output);(f/'silkscreen-construction.json').write_text(json.dumps(annotation,indent=2)+'\n')
report=dict(scope='Separate 68uF hybrid-bulk routing construction; every electrical pin/net/source-trace identity retained',source_sha256=hashlib.sha256(raw).hexdigest(),circuit_sha256=hashlib.sha256(output).hexdigest(),inherited_routing_source='src/compact/six-layer-routing.json',inherited_routing_sha256=hashlib.sha256(route_path.read_bytes()).hexdigest(),all_other_component_values_unchanged=True,all_326_port_identities_and_net_intents_unchanged=True,mandatory_new_checks=['native DRC with exact filled/capped policy','all-six-layer independent copper and every-pin physical graph','clock/USB/thermal review','CAM, exact new BOM/CPL and native assembly'],manufacturing_release=False)
(f/'hybrid-candidate-construction.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
