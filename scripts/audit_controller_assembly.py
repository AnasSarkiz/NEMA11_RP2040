#!/usr/bin/env python3
"""Independent genuine STEP solids at native CAD poses; nominal geometry only."""
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path
import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
compact='--compact' in sys.argv
folder=sys.argv[sys.argv.index('--folder')+1] if '--folder' in sys.argv else 'artifacts/compact-controller' if compact else 'artifacts/controller'
path = ROOT / folder / 'unrouted.circuit.json'
records = json.loads(path.read_text())
names = {e['source_component_id']: e['name'] for e in records if e['type'] == 'source_component'}
pcb = {e['pcb_component_id']: e for e in records if e['type'] == 'pcb_component'}
cache, parts, rows, errors = {}, {}, [], []
for e in records:
    if e['type'] != 'cad_component' or not e.get('model_step_url'):
        continue
    if pcb[e['pcb_component_id']].get('do_not_place'):
        continue
    name = names[e['source_component_id']]
    local = ROOT / 'imports' / e['model_step_url'].split('/imports/')[1]
    if local not in cache:
        cache[local] = cq.importers.importStep(str(local)).val()
    shape = cache[local]
    if not shape.isValid():
        errors.append({'part': name, 'invalid_original_supplier_STEP': str(local.relative_to(ROOT))})
    assert shape.Volume() > 0, name
    origin = e.get('model_origin_position', dict(x=0, y=0, z=0))
    shape = shape.translate(tuple(-origin[k] for k in 'xyz'))
    for axis, vector in [('x', (1,0,0)), ('y', (0,1,0)), ('z', (0,0,1))]:
        if e['rotation'][axis]:
            shape = shape.rotate((0,0,0), vector, e['rotation'][axis])
    shape = shape.translate(tuple(e['position'][k] for k in 'xyz'))
    b = shape.BoundingBox()
    rows.append({'part': name, 'model': str(local.relative_to(ROOT)),
                 'bounds_mm': [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]})
    parts[name] = shape
expected_count=76 if '--no-buzzer' in sys.argv else 82
assert len(parts) == expected_count, len(parts)
bounds = {e['part']: e['bounds_mm'] for e in rows}
pairs = []
for a, b in itertools.combinations(parts, 2):
    aa, bb = bounds[a], bounds[b]
    lower = math.sqrt(sum(max(aa[i]-bb[i+3], bb[i]-aa[i+3], 0)**2 for i in range(3)))
    if lower > .5:
        continue
    distance = parts[a].distance(parts[b])
    pairs.append({'a': a, 'b': b, 'nominal_surface_gap_mm': distance})
    if lower < 1e-8:
        volume = max(0, parts[a].intersect(parts[b]).Volume())
        if volume > 1e-5:
            errors.append({'a': a, 'b': b, 'solid_collision_mm3': volume})

alignments = []
for name in ['J_MOTOR', 'J_PD', 'J_DATA']:
    cad = next(e for e in records if e['type'] == 'cad_component' and names[e['source_component_id']] == name)
    holes = [e for e in records if e['type'] == 'pcb_plated_hole' and e['pcb_component_id'] == cad['pcb_component_id']]
    z=.4 if name in ['J_PD','J_DATA'] else 0
    slab=cq.Workplane('XY').box(100,100,.2).translate((0,0,z)).val()
    if name in ['J_PD','J_DATA']:
        holes += [e for e in records if e['type']=='pcb_hole' and e.get('pcb_component_id')==cad['pcb_component_id']]
    leads = [s.Center().toTuple()[:2] for s in parts[name].intersect(slab).Solids()]
    assert len(leads) == len(holes) == (6 if name in ['J_PD','J_DATA'] else 4), (name, leads)
    assignments = []
    for xy in leads:
        hole = min(holes, key=lambda h: math.dist(xy, (h['x'], h['y'])))
        error = math.dist(xy, (hole['x'], hole['y']))
        assignments.append({'hole': hole[hole['type']+'_id'], 'lead_xy_mm': xy, 'centre_error_mm': error})
        if error > .05:
            errors.append({'part': name, 'lead_to_hole_error_mm': error})
    assert len({e['hole'] for e in assignments}) == len(holes)
    alignments.append({'part': name, 'section_z_mm': [z-.1,z+.1], 'leads_and_locating_pegs': assignments})

# Include the actual PCB material, not just component-to-component collisions.
# The original GCT import omitted a locating hole and would otherwise appear
# collision-free despite its plastic peg intersecting the laminate.
board = next(e for e in records if e['type']=='pcb_board')
outline = [(p['x'],p['y']) for p in board['outline']]
laminate = cq.Workplane('XY').polyline(outline).close().extrude(1.56).translate((0,0,-.78)).val()
for e in records:
    if e['type'] not in ['pcb_hole','pcb_plated_hole']:
        continue
    diameter=e.get('hole_diameter')
    if diameter:
        tool=cq.Solid.makeCylinder(diameter/2,3,cq.Vector(e['x'],e['y'],-1.5))
    else:
        w,h=e['hole_width'],e['hole_height']
        angle=(90 if h>w else 0)+e.get('ccw_rotation',0)
        tool=cq.Workplane('XY').slot2D(max(w,h),min(w,h),angle).extrude(3).translate((e['x'],e['y'],-1.5)).val()
    laminate=laminate.cut(tool)
PCB_intersections=[]
for name,shape in parts.items():
    if bounds[name][2] >= .78:
        continue
    volume=max(0,shape.intersect(laminate).Volume())
    PCB_intersections.append({'part':name,'laminate_interference_mm3':volume})
    if volume>1e-5:
        errors.append({'part':name,'PCB_laminate_interference_mm3':volume})

report = {'scope': f'{expected_count} fitted supplier STEP solids; nominal PCB assembly, excluding motor/carrier/harness/hardware',
          'circuit_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
          'parts': rows, 'nearby_pairs': pairs, 'connector_lead_sections': alignments,
          'PCB_material_intersections':PCB_intersections,
          'PCB_surface_CAD_allowance_mm':.02,
          'errors': errors, 'manufacturer_tolerances_verified': False,
          'nominal_solid_and_lead_fit_pass':not any('invalid_original_supplier_STEP' not in e for e in errors),
          'all_original_supplier_STEP_valid':not any('invalid_original_supplier_STEP' in e for e in errors),
          'physical_assembly_tested': False, 'manufacturing_release': False}
if compact:
    report['fitted_part_frame_XY_mm']=[min(r['bounds_mm'][i] for r in rows) for i in [0,1]]+[max(r['bounds_mm'][i] for r in rows) for i in [3,4]]
    report['all_fitted_on_top']=all(pcb[e['pcb_component_id']]['layer']=='top' for e in records if e['type']=='cad_component' and not pcb[e['pcb_component_id']].get('do_not_place'))
    frame=report['fitted_part_frame_XY_mm']
    report['whole_fitted_parts_within_28_3mm_frame']=frame[0]>=-14.15 and frame[1]>=-14.15 and frame[2]<=14.15 and frame[3]<=14.15
    if not report['whole_fitted_parts_within_28_3mm_frame']:report['errors'].append({'frame_violation':frame})
(ROOT / folder / 'nominal-assembly-audit.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'supplier_solids': len(parts), 'connector_lead_rows_checked': 3, 'errors': errors}))
raise SystemExit(bool(errors))
