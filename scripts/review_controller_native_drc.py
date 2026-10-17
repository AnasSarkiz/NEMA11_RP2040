#!/usr/bin/env python3
"""Require zero current DRC errors; retain historical stock-checker diagnosis."""
import hashlib
import json
from pathlib import Path
from shapely.geometry import Point
from shapely.ops import unary_union
from pcb_geometry import Copper

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/controller-pcb'
path = OUT / 'board.circuit.json'
sha = hashlib.sha256(path.read_bytes()).hexdigest()
native = json.loads((OUT / 'native-drc.json').read_text())
physical = json.loads((OUT / 'independent-copper-audit.json').read_text())
assert native['circuit_sha256'] == physical['circuit_sha256'] == sha
assert not physical['errors']
assert native['native_drc_pass'] and not native['errors'], 'Every native DRC error is fatal'
stock = json.loads((OUT / 'native-drc-stock-0.0.242.json').read_text())
assert stock['circuit_sha256'] == sha, 'Historical comparison is for a different PCB'
records = json.loads(path.read_text())
geometry = {}
for e, _, shapes in Copper(records).elements():
    geometry.setdefault(e[e['type']+'_id'], []).extend(shapes.values())
keepouts = {e['pcb_keepout_id']:e for e in records if e['type']=='pcb_keepout'}
reviewed, unresolved = [], []
for error in stock['errors']:
    identifier = error.get('pcb_trace_id')
    match = next(((k,e) for k,e in keepouts.items() if error.get('pcb_trace_error_id','').endswith('_'+k)
                  and 'keepout' in error.get('message','')),None)
    if not match or identifier not in geometry:
        unresolved.append(error)
        continue
    ko, e = match
    assert e['shape']=='circle'
    circle = Point(e['center']['x'],e['center']['y']).buffer(e['radius'],quad_segs=256)
    copper = unary_union(geometry[identifier])
    gap = copper.distance(circle)
    overlap = copper.intersection(circle).area
    assert overlap < 1e-9, (identifier,ko,overlap)
    assert gap >= .15-2e-6, (identifier,ko,gap)
    reviewed.append({'native_error_id':error['pcb_trace_error_id'], 'copper':identifier,'keepout':ko,
                     'actual_circle_gap_mm':gap, 'actual_circle_overlap_mm2':overlap,
                     'reason':'Native trace checker uses the circle bounding rectangle; actual circular keepout is clear'})
report = {'scope':'Zero native DRC errors required; exact circle-distance tool correction and historical stock comparison retained',
          'circuit_sha256':sha,'raw_native_error_count':len(native['errors']),'waived_or_filtered_errors':[],
          'historical_stock_error_count':len(stock['errors']),
          'historical_stock_circular_keepout_false_positives':reviewed,'unresolved_errors':unresolved,
          'reviewed_DRC_pass':not unresolved,'manufacturing_release':False}
(OUT / 'native-drc-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'native_DRC_errors':len(native['errors']),'historical_circle_bbox_errors':len(reviewed),'unresolved_errors':len(unresolved)}))
raise SystemExit(bool(unresolved))
