#!/usr/bin/env python3
"""Actual coupled copper and full-width adjacent ground, adapted from v1.13."""
import hashlib
import json
import math
from pathlib import Path
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union
from pcb_geometry import Copper

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'artifacts/controller-pcb/board.circuit.json'
records=json.loads(path.read_text())
plan=json.loads((ROOT/'config/controller-usb-track-plan.json').read_text())
copper=Copper(records)
nets={name:key for key,name in copper.nets.items()}
elements=copper.elements()
ground_members,ground_roots=copper.groups(nets['GND'],elements)
ground_pad_roots={root for (e,_,_),root in zip(ground_members,ground_roots) if e['type'] in ['pcb_smtpad','pcb_plated_hole']}
assert len(ground_pad_roots)==1, 'Ground pads are not in one actual copper network'
ground_pours={e['pcb_copper_pour_id'] for (e,_,_),root in zip(ground_members,ground_roots)
              if e['type']=='pcb_copper_pour' and root in ground_pad_roots}
rows,errors=[],[]
for core in plan['cores']:
    reference=unary_union([shapes[core['reference_layer']] for e,k,shapes in elements
                           if e['type']=='pcb_copper_pour' and e['pcb_copper_pour_id'] in ground_pours and core['reference_layer'] in shapes])
    keys={nets[t['net']] for t in core['tracks']}
    transitions=unary_union([Point(e['x'],e['y']).buffer(e['outer_diameter']/2+.21) for e in records
                             if e['type']=='pcb_via' and copper.key(e) in keys])
    tracks,lines=[],[]
    for track in core['tracks']:
        identifier='controller_'+track['trace_id']
        e=next(e for e in records if e.get('pcb_trace_id')==identifier)
        points=[(p['x'],p['y']) for p in e['route']]
        if points!=[tuple(p) for p in track['points']] or any(p.get('layer')!=core['layer'] or p.get('width')!=.25 for p in e['route']):
            errors.append({'coupled_track_changed':identifier})
        line=LineString(points)
        lines.append(line)
        screened=line.difference(transitions)
        missing=screened.difference(reference.buffer(.000002))
        width=line.buffer(.125).difference(transitions)
        unsupported=width.difference(reference.buffer(.000002))
        if missing.length>1e-6 or unsupported.area>1e-6:
            errors.append({'reference_gap':identifier,'length_mm':missing.length,'copper_area_mm2':unsupported.area})
        tracks.append({'trace':identifier,'length_mm':line.length,'screened_length_mm':screened.length,
                       'unsupported_reference_length_mm':missing.length,'unsupported_full_width_reference_mm2':unsupported.area})
    gap=lines[0].distance(lines[1])-.25
    skew=abs(lines[0].length-lines[1].length)
    if gap<.15-.000002 or skew>.5:
        errors.append({'pair_geometry':core['name'],'clearance_mm':gap,'skew_mm':skew})
    rows.append({'core':core['name'],'layer':core['layer'],'reference_layer':core['reference_layer'],
                 'minimum_pair_clearance_mm':gap,'length_skew_mm':skew,'tracks':tracks})
for e in records:
    if e['type']=='pcb_trace' and copper.nets.get(copper.key(e)) in ['USB_DP','USB_DM','MCU_DP','MCU_DM']:
        if any(p.get('layer') in ['inner1','inner2'] for p in e['route']):
            errors.append({'USB_inner_signal_layer':e['pcb_trace_id']})
report={'scope':'Preserved actual USB pair tracks and full-width adjacent grounded reference',
        'circuit_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'cores':rows,
        'transition_exceptions':'Only actual same-pair via antipads, via pad radius plus 0.21 mm',
        'errors':errors,'passed':not errors,'controlled_impedance_verified':False,
        'fabricator_stackup_approved':False,'USB_hardware_operation_verified':False,'manufacturing_release':False}
(path.parent/'USB-reference-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'USB_coupled_cores':len(rows),'errors':errors}))
raise SystemExit(bool(errors))
