#!/usr/bin/env python3
"""Actual solid collisions for the proposed carrier; purchasing/tolerances separate."""
import hashlib
import json
from pathlib import Path
import cadquery as cq

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'imports/mechanical/nema11-front-carrier.step'
carrier = cq.importers.importStep(str(path)).val()
motor = cq.importers.importStep(str(ROOT / 'imports/motor/11HS12-0674S.step')).val()
motor = motor.rotate((0,0,0), (0,0,1), 90).translate((0,0,-42))
records = json.loads((ROOT / 'artifacts/controller/unrouted.circuit.json').read_text())
board = cq.Workplane('XY').box(35,40,1.6).translate((0,2.5,0)).val()
for x in [-13,13]:
    for y in [-13,13]:
        board = board.cut(cq.Solid.makeCylinder(1.6,2,cq.Vector(x,y,-1)))
tests = [('OEM motor with actual lead stubs',motor), ('PCB',board)]
nominal = json.loads((ROOT / 'artifacts/controller/nominal-assembly-audit.json').read_text())
names = {e['source_component_id']: e['name'] for e in records if e['type']=='source_component'}
for row in nominal['parts']:
    if row['bounds_mm'][2] > -.799:
        continue
    name = row['part']
    cad = next(e for e in records if e['type']=='cad_component' and names[e['source_component_id']]==name)
    shape = cq.importers.importStep(str(ROOT / row['model'])).val()
    origin = cad.get('model_origin_position',dict(x=0,y=0,z=0))
    shape = shape.translate(tuple(-origin[k] for k in 'xyz'))
    for axis, direction in [('x',(1,0,0)),('y',(0,1,0)),('z',(0,0,1))]:
        if cad['rotation'][axis]:
            shape = shape.rotate((0,0,0),direction,cad['rotation'][axis])
    shape = shape.translate(tuple(cad['position'][k] for k in 'xyz'))
    tests.append((name,shape))
rows, errors = [], []
for name, shape in tests:
    volume = max(0,carrier.intersect(shape).Volume())
    rows.append({'part':name,'interference_mm3':volume,'surface_gap_mm':carrier.distance(shape)})
    if volume > 1e-5:
        errors.append({'part':name,'interference_mm3':volume})
report = {'scope':'Nominal front carrier proposal versus actual OEM motor, PCB and underside supplier solids',
          'carrier_STEP_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
          'tests':rows,'errors':errors,'nominal_collision_check_pass':not errors,
          'rear_motor_attachment_assumed':False,'fasteners_or_full_harness_verified':False,
          'tolerances_strength_and_physical_assembly_verified':False,'manufacturing_release':False}
(ROOT / 'artifacts/requirements/front-carrier-collision-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'nominal_solid_checks':len(rows),'errors':errors}))
raise SystemExit(bool(errors))
