#!/usr/bin/env python3
"""Nominal supplier-solid assembly check driven by native CAD poses."""
import hashlib, itertools, json, math
from pathlib import Path
import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
path = ROOT/'artifacts/rp2040-pcb/board.circuit.json'
records = json.loads(path.read_text())
names = {e['source_component_id']: e['name'] for e in records if e['type'] == 'source_component'}
parts, cache, rows, errors = {}, {}, [], []
for e in records:
    if e['type'] != 'cad_component' or not e.get('model_step_url'):
        continue
    assert e.get('model_unit_to_mm_scale_factor', 1) == 1
    name = names[e['source_component_id']]
    local = ROOT/'imports/supplier'/e['model_step_url'].split('/imports/supplier/')[1]
    if local not in cache:
        cache[local] = cq.importers.importStep(str(local)).val()
    shape = cache[local]
    assert shape.isValid() and shape.Volume() > 0
    origin = e.get('model_origin_position', dict(x=0,y=0,z=0))
    shape = shape.translate(tuple(-origin[k] for k in 'xyz'))
    for axis, vector in [('x',(1,0,0)), ('y',(0,1,0)), ('z',(0,0,1))]:
        if e['rotation'][axis]:
            shape = shape.rotate((0,0,0), vector, e['rotation'][axis])
    shape = shape.translate(tuple(e['position'][k] for k in 'xyz'))
    bounds = shape.BoundingBox()
    row = {'part': name, 'supplier_model': str(local.relative_to(ROOT)),
           'bounds_mm': [bounds.xmin,bounds.ymin,bounds.zmin,bounds.xmax,bounds.ymax,bounds.zmax]}
    rows.append(row)
    if bounds.zmin < .8 - .025:
        errors.append({'part': name, 'nominal_model_below_PCB_surface_mm': .8-bounds.zmin})
    if min(bounds.xmin, bounds.ymin) < -17.25 or max(bounds.xmax, bounds.ymax) > 17.25:
        errors.append({'part': name, 'model_outside_development_edge_inset': True})
    parts[name] = shape
bounds = {e['part']: e['bounds_mm'] for e in rows}
minimum = math.inf
pairs = []
for a, b in itertools.combinations(parts, 2):
    aa, bb = bounds[a], bounds[b]
    lower = math.sqrt(sum(max(aa[i]-bb[i+3],bb[i]-aa[i+3],0)**2 for i in range(3)))
    if lower > 1.:
        continue
    distance = parts[a].distance(parts[b])
    minimum = min(minimum, distance)
    pairs.append({'a': a, 'b': b, 'nominal_surface_gap_mm': distance})
    if lower < 1e-8:
        volume = max(0, parts[a].intersect(parts[b]).Volume())
        if volume > 1e-6:
            errors.append({'a': a, 'b': b, 'solid_collision_mm3': volume})
assert len(parts) == 24
report = {'scope': '24 MCU subsystem supplier solids at native tscircuit CAD poses',
          'circuit_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'parts': rows,
          'nearby_pairs': pairs, 'minimum_nominal_component_gap_mm': minimum, 'errors': errors,
          'manufacturer_tolerance_envelopes_verified': False, 'solder_and_rework_access_verified': False,
          'motor_fastener_JST_harness_assembly_included': False, 'manufacturing_release': False}
(ROOT/'artifacts/rp2040-pcb/nominal-assembly-audit.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({'supplier_solids': len(parts), 'minimum_nominal_gap_mm': minimum, 'errors': errors}))
raise SystemExit(bool(errors))
