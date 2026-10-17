#!/usr/bin/env python3
"""All-pin copper connectivity from a physical graph, independent of net labels."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from shapely.strtree import STRtree
from pcb_geometry import Copper, LAYERS

ROOT=Path(__file__).resolve().parents[1]


def inspect(records):
    copper=Copper(records)
    elements=copper.elements()
    parent=list(range(len(elements)))
    def root(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]];i=parent[i]
        return i
    def union(a,b):
        a,b=root(a),root(b)
        if a!=b:parent[b]=a
    # Unlike a logical connectivity map, this union includes foreign-net and NC
    # copper too. Only actual same-layer metal intersection joins nodes. One
    # plated-barrel node carries its real annulus on every declared layer.
    for layer in LAYERS:
        local=[(i,shapes[layer]) for i,(_,_,shapes) in enumerate(elements) if layer in shapes]
        tree=STRtree([shape for _,shape in local])
        for j,(owner,shape) in enumerate(local):
            for k in tree.query(shape,predicate='intersects'):
                if k>j:union(owner,local[k][0])
    roots=[root(i) for i in range(len(elements))]
    errors=[]
    nodes_by_root=defaultdict(list)
    pad_by_port=defaultdict(list)
    for i,(e,_,_) in enumerate(elements):
        nodes_by_root[roots[i]].append(i)
        if e['type'] in ['pcb_smtpad','pcb_plated_hole']:
            pad_by_port[e['pcb_port_id']].append(i)
    source_ports={e['source_port_id']:e for e in records if e['type']=='source_port'}
    source_components={e['source_component_id']:e for e in records if e['type']=='source_component'}
    pcb_components={e['source_component_id']:e for e in records if e['type']=='pcb_component'}
    pcb_ports=defaultdict(list)
    for p in records:
        if p['type']=='pcb_port':pcb_ports[p['source_port_id']].append(p)
    net_roots=defaultdict(set)
    root_ports=defaultdict(list)
    rows=[]
    for p in source_ports.values():
        component=source_components[p['source_component_id']]
        qualified=f"{component['name']}.{p['pin_number']}"
        key=p.get('subcircuit_connectivity_map_key')
        nc=p.get('do_not_connect',False)
        if bool(key)==bool(nc):errors.append({'type':'ambiguous_pin_intent','pin':qualified})
        candidates=pcb_ports[p['source_port_id']]
        pads=pad_by_port[candidates[0]['pcb_port_id']] if len(candidates)==1 else []
        if len(candidates)!=1 or len(pads)!=1:
            errors.append({'type':'missing_or_duplicate_physical_pad','pin':qualified,
                           'PCB_ports':len(candidates),'pads':len(pads)})
            continue
        node=pads[0];group=roots[node];pad=elements[node][0]
        root_ports[group].append(qualified)
        if key:net_roots[key].add(group)
        pcb=pcb_components[p['source_component_id']]
        assembly=('bare_PCB_test_point' if component['ftype']=='simple_test_point' else
                  'optional_encoder_DNP' if pcb.get('do_not_place') else
                  'manual_PH_header' if component['name']=='J_MOTOR' else 'fitted_SMT')
        rows.append({'designator':component['name'],'pin':p['pin_number'],'pin_name':p['name'],
                     'net':copper.nets.get(key),'assembly':assembly,
                     'state':'intentional_NC' if nc else 'required_connection',
                     'source_port_id':p['source_port_id'],'pcb_port_id':candidates[0]['pcb_port_id'],
                     'pad_id':pad[pad['type']+'_id'],'layers':sorted(elements[node][2]),'_root':group})
        if nc and len(nodes_by_root[group])!=1:
            errors.append({'type':'intentional_NC_has_copper_contact','pin':qualified})
    for group,nodes in nodes_by_root.items():
        keys={elements[i][1] for i in nodes if elements[i][1] is not None}
        if len(keys)>1:errors.append({'type':'short','nets':sorted(copper.nets.get(k,k) for k in keys),
                                      'pins':sorted(root_ports[group])})
    nets=[]
    for key,name in copper.nets.items():
        groups=net_roots[key]
        pins=sorted(f"{r['designator']}.{r['pin']}" for r in rows if r['net']==name)
        if len(groups)!=1:errors.append({'type':'open_net','net':name,'physical_islands':len(groups),'pins':pins})
        nets.append({'name':name,'physical_islands':len(groups),'physical_terminal_count':len(pins),'pins':pins})
    canonical={g:'physical_island_'+str(i) for i,g in enumerate(sorted(nodes_by_root,key=lambda g:sorted(root_ports[g])))}
    for row in rows:
        group=row.pop('_root');row['copper_island']=canonical[group]
        row['island_terminal_count']=len(root_ports[group])
    components=[]
    for c in source_components.values():
        pins=[r for r in rows if r['designator']==c['name']]
        components.append({'designator':c['name'],'assembly':pins[0]['assembly'] if pins else 'missing_physical_pins',
                           'physical_pins':len(pins),'required_connections':sum(r['state']=='required_connection' for r in pins),
                           'intentional_NC':sum(r['state']=='intentional_NC' for r in pins)})
    return {'method':'Global physical copper graph; foreign net labels and NC never imply or prevent a metal contact',
            'components_checked':len(source_components),'physical_pins_checked':len(rows),
            'required_connected_pins':sum(r['state']=='required_connection' for r in rows),
            'intentional_NC_pins':sum(r['state']=='intentional_NC' for r in rows),
            'nets_checked':len(nets),'opens':sum(e['type']=='open_net' for e in errors),
            'shorts':sum(e['type']=='short' for e in errors),'components':components,'nets':nets,'pins':rows,
            'errors':errors,'passed':not errors,'manufacturing_release':False}


if __name__=='__main__':
    path=ROOT/'artifacts/controller-pcb/board.circuit.json'
    report=inspect(json.loads(path.read_text()))
    assert report['components_checked']==92 and report['physical_pins_checked']==341
    assert report['required_connected_pins']==304 and report['intentional_NC_pins']==37 and report['nets_checked']==64
    report['circuit_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    (path.parent/'all-pin-connectivity.json').write_text(json.dumps(report,indent=2)+'\n')
    with (path.parent/'all-pin-connectivity.csv').open('w',newline='') as f:
        fields=['designator','pin','pin_name','net','assembly','state','pad_id','copper_island','island_terminal_count','layers']
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
        for row in report['pins']:w.writerow({**row,'layers':'+'.join(row['layers'])})
    print(json.dumps({k:v for k,v in report.items() if k not in ['components','nets','pins']}))
    raise SystemExit(bool(report['errors']))
