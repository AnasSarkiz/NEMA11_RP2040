#!/usr/bin/env python3
"""Independent full-controller copper, drilled geometry and mounting keepouts."""
import argparse
import hashlib
import json
from pathlib import Path
from collections import Counter
from shapely.geometry import Point
from shapely.strtree import STRtree
from audit_core_pcb import audit
from pcb_geometry import Copper, pad_shape

ROOT = Path(__file__).resolve().parents[1]


def inspect(records):
    report = audit(records)
    copper = Copper(records)
    elements = copper.elements()
    errors = report['errors']
    for key,name in copper.nets.items():
        members,roots=copper.groups(key,elements)
        anchored={root for (e,_,_),root in zip(members,roots) if e['type'] in ['pcb_smtpad','pcb_plated_hole']}
        unanchored={e[e['type']+'_id'] for (e,_,_),root in zip(members,roots) if root not in anchored}
        if unanchored:
            errors.append({'type':'unanchored_copper','net':name,'ids':sorted(unanchored)})
    for e in records:
        if e['type'] != 'pcb_keepout':
            continue
        if e.get('shape') == 'circle':
            c = e['center']; shape = Point(c['x'],c['y']).buffer(e['radius'], quad_segs=128)
        else:
            raise ValueError('Unreviewed full-controller keepout geometry')
        for record, key, shapes in elements:
            if any(layer in e['layers'] and shape.intersection(g).area > 1e-9 for layer,g in shapes.items()):
                errors.append({'type':'mounting_keepout', 'keepout':e['pcb_keepout_id'],
                               'id':record[record['type']+'_id']})
    drills = []
    for e in records:
        if e['type'] not in ['pcb_hole','pcb_plated_hole','pcb_via']:
            continue
        hole = {**e,'shape':'circle' if e['type'] in ['pcb_hole','pcb_via'] else e['shape'],
                'width':e.get('hole_width',e.get('hole_diameter')),
                'height':e.get('hole_height',e.get('hole_diameter'))}
        drills.append((e,copper.key(e) if e['type'] != 'pcb_hole' else None,pad_shape(hole)))
    minimum_drill_gap = float('inf')
    for i,(a,ka,sa) in enumerate(drills):
        for b,kb,sb in drills[i+1:]:
            gap=sa.distance(sb)
            minimum_drill_gap=min(minimum_drill_gap,gap)
            rule=.2 if 'pcb_via' in [a['type'],b['type']] else .45
            if gap < rule-2e-6:
                errors.append({'type':'drill_pair_clearance','a':a[a['type']+'_id'],
                               'b':b[b['type']+'_id'],'gap_mm':gap,'minimum_mm':rule})
    # Pads on the same plated barrel are its own copper. All foreign copper
    # must clear the real circular/slot drill, independently of annular rings.
    flat=[(r,k,l,s) for r,k,shapes in elements for l,s in shapes.items()]
    tree=STRtree([s for _,_,_,s in flat])
    seen=set()
    for hole,key,shape in drills:
        hid=hole[hole['type']+'_id']
        for idx in tree.query(shape.buffer(.30)):
            record,other,layer,metal=flat[idx]
            rid=record[record['type']+'_id']
            if rid == hid or key is not None and key == other:
                continue
            pair=(hid,rid,layer)
            if pair in seen:continue
            seen.add(pair)
            gap=shape.distance(metal)
            minimum=.30 if hole['type']=='pcb_plated_hole' and layer.startswith('inner') else .20
            if gap < minimum-2e-6:
                errors.append({'type':'drill_to_foreign_copper','drill':hid,'copper':rid,'layer':layer,'gap_mm':gap,'minimum_mm':minimum})
    report.update(scope='Full controller physical copper; no symbolic net IDs substitute for contact',
                  error_counts=dict(Counter(e['type'] for e in errors)),
                  actual_drilled_objects_checked=len(drills),minimum_declared_drill_pair_gap_mm=minimum_drill_gap,
                  manufacturing_release=False)
    return report


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=ROOT/'artifacts/controller-pcb/board.circuit.json');a=p.parse_args()
    report=inspect(json.loads(a.input.read_text()));report['circuit_sha256']=hashlib.sha256(a.input.read_bytes()).hexdigest()
    output=a.input.parent/('construction-audit.json' if a.input.name == 'seeded.circuit.json' else 'independent-copper-audit.json')
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'errors':len(report['errors']),'error_counts':report['error_counts']}))
    raise SystemExit(bool(report['errors']))
