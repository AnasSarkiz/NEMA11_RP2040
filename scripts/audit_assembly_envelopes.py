#!/usr/bin/env python3
"""Conditional hardware/tool/plug envelopes against actual supplier solids."""
import hashlib
import json
import math
from pathlib import Path
import cadquery as cq

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'artifacts/controller/unrouted.circuit.json'
records=json.loads(source.read_text())
audit=json.loads((ROOT/'artifacts/controller/nominal-assembly-audit.json').read_text())
assert audit['circuit_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
names={e['source_component_id']:e['name'] for e in records if e['type']=='source_component'}
cad={names[e['source_component_id']]:e for e in records if e['type']=='cad_component'}
cache={}


def part(row):
    if row['part'] in cache:return cache[row['part']]
    shape=cq.importers.importStep(str(ROOT/row['model'])).val()
    pose=cad[row['part']];origin=pose.get('model_origin_position',dict(x=0,y=0,z=0))
    shape=shape.translate(tuple(-origin[k] for k in 'xyz'))
    for key,axis in [('x',(1,0,0)),('y',(0,1,0)),('z',(0,0,1))]:
        if pose['rotation'][key]:shape=shape.rotate((0,0,0),axis,pose['rotation'][key])
    shape=shape.translate(tuple(pose['position'][k] for k in 'xyz'))
    cache[row['part']]=shape
    return shape


envelopes=[]
for x in [-13,13]:
    for y in [-13,13]:
        envelopes.append((f'PCB head {x},{y}',cq.Solid.makeCylinder(2.25,2.5,cq.Vector(x,y,.8))))
        envelopes.append((f'2 mm hex-key approach {x},{y}',cq.Solid.makeCylinder(1.5,22,cq.Vector(x,y,3.3))))
for name in ['J_PD','J_DATA']:
    pose=cad[name]['position']
    envelopes.append((f'{name} maximum USB overmold',cq.Workplane('XY').box(10,8,15).translate((pose['x'],pose['y'],8.26+7.5)).val()))
rows,errors,separations=[],[],[]
for label,shape in envelopes:
    b=shape.BoundingBox();bb=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
    minimum_bbox_gap=math.inf
    for row in audit['parts']:
        a=row['bounds_mm']
        minimum_bbox_gap=min(minimum_bbox_gap,math.sqrt(sum(max(a[i]-bb[i+3],bb[i]-a[i+3],0)**2 for i in range(3))))
        if any(a[i]>bb[i+3] or bb[i]>a[i+3] for i in range(3)):continue
        volume=max(0,shape.intersect(part(row)).Volume())
        rows.append({'envelope':label,'part':row['part'],'interference_mm3':volume})
        if volume>1e-5:errors.append(rows[-1])
    separations.append({'envelope':label,'supplier_parts_screened':len(audit['parts']),
                        'minimum_AABB_separation_mm':minimum_bbox_gap})
# Header and plug intentionally mate. Their external maximum housing envelope
# is screened only against the independent USB overmold and hardware envelopes.
housing=cq.Workplane('XY').box(9.8,5,8).translate((11.5,19.2,4.8)).val()
for label,shape in envelopes:
    volume=max(0,housing.intersect(shape).Volume())
    if volume>1e-5:errors.append({'mating_PH_housing_envelope_vs':label,'interference_mm3':volume})
report={'scope':'Required maximum hardware/plug envelopes; these are not purchased-part supplier CAD',
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'PCB_head_maximum_diameter_height_mm':[4.5,2.5],
        'hex_key_shaft_clearance_diameter_mm':3,'hex_key_size_across_flats_mm':2,
        'USB_cable_overmold_maximum_width_depth_mm':[10,8],
        'PH_mated_housing_screen_mm':[9.8,5,8],
        'nominal_head_tool_and_plug_envelope_checks':rows,'errors':errors,'envelope_check_pass':not errors,
        'supplier_bounds_screens':separations,
        'candidate_front_screw':'M2.5 x 4','candidate_PCB_screw':'M2.5 x 5',
        'required_front_screw_length_range_mm':[3.7,4.1],
        'required_front_plate_thickness_range_mm':[.9,1.1],
        'front_thread_engagement_range_mm':[2.6,3.2],
        'motor_minimum_tapped_depth_mm':3.5,
        'PCB_thread_engagement_range_mm_for_4_7_to_5_1mm_screw_and_1_44_to_1_60mm_PCB':[3.1,3.66],
        'carrier_threaded_depth_mm':5,
        'actual_supplier_fasteners_USB_cables_and_PH_plug_models_verified':False,
        'physical_insertion_torque_crimp_and_retention_verified':False,'manufacturing_release':False}
(ROOT/'artifacts/requirements/assembly-envelope-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'conditional_envelopes_checked':len(envelopes),'errors':errors}))
raise SystemExit(bool(errors))
